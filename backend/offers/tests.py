# backend/offers/tests.py

"""
Offer tests — the offers API
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Check the offers API as the frontend will use it: anyone reads the published
offers, filtered, ordered and paged; an employer creates, edits, publishes,
closes and deletes their own offers and nobody else's; the rules of the
fields and of the states hold; a candidate and a visitor are kept out of
the management.
"""

import json
from datetime import timedelta

from django.core.cache import cache
from django.test import Client, TestCase
from django.utils import timezone

from accounts.models import User
from profiles.models import EmployerProfile

from .models import JobOffer

PASSWORD = "Correct-horse-9"

# What a valid new offer needs; the tests change one field at a time
OFFER = {
    "title": "Python developer",
    "description": "Django and Vue, in a small team.",
    "city": "Geneva",
    "country": "CH",
    "contract": "permanent",
}


class OfferApiTests(TestCase):
    """The public list and detail, and the management by the employers."""

    def setUp(self):
        cache.clear()
        self.candidate = User.objects.create_user(
            email="cand@example.com", password=PASSWORD, role="candidate"
        )
        self.employer = User.objects.create_user(
            email="emp@example.com", password=PASSWORD, role="employer"
        )
        self.other = User.objects.create_user(
            email="other@example.com", password=PASSWORD, role="employer"
        )
        # Profiles with a company, as the profile page would have made them
        self.company = EmployerProfile.objects.create(user=self.employer, company_name="Acme")
        self.other_company = EmployerProfile.objects.create(user=self.other, company_name="Globex")

    # ── Helpers ───────────────────────────────────────────────────────

    def login(self, user):
        """A client logged in as the user, with the CSRF token a browser
        would send back (enforced, as in the other API tests)."""
        client = Client(enforce_csrf_checks=True)
        client.force_login(user)
        client.get("/_allauth/browser/v1/auth/session")
        client.defaults["HTTP_X_CSRFTOKEN"] = client.cookies["csrftoken"].value
        return client

    def post(self, client, url, data=None):
        return client.post(url, data=json.dumps(data or {}), content_type="application/json")

    def patch(self, client, url, data):
        return client.patch(url, data=json.dumps(data), content_type="application/json")

    def offer(self, employer=None, status="published", **fields):
        """An offer in the database, published unless said otherwise."""
        values = {**OFFER, **fields}
        return JobOffer.objects.create(employer=employer or self.company, status=status, **values)

    # ── Reading, for anyone ───────────────────────────────────────────

    def test_the_public_list_shows_the_published_offers_only(self):
        self.offer(title="Published")
        self.offer(title="Draft", status="draft")
        self.offer(title="Closed", status="closed")
        response = Client().get("/api/offers/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 1)
        offer = data["results"][0]
        self.assertEqual(offer["title"], "Published")
        self.assertEqual(offer["status"], "published")
        # The company comes from the profile of the employer, not from the offer
        self.assertEqual(offer["company"], {"name": "Acme", "logo": None})
        self.assertEqual(offer["currency"], "CHF")
        self.assertIsNotNone(offer["published_at"])

    def test_the_list_is_newest_first_and_can_be_ordered(self):
        old = self.offer(title="Old")
        old.published_at = timezone.now() - timedelta(days=3)
        old.save()
        self.offer(title="New", salary_min=5000, salary_period="month")
        titles = [o["title"] for o in Client().get("/api/offers/").json()["results"]]
        self.assertEqual(titles, ["New", "Old"])
        titles = [o["title"] for o in Client().get("/api/offers/?ordering=title").json()["results"]]
        self.assertEqual(titles, ["New", "Old"])
        titles = [o["title"] for o in Client().get("/api/offers/?ordering=published_at").json()["results"]]
        self.assertEqual(titles, ["Old", "New"])

    def test_the_list_is_filtered_by_the_query_string(self):
        self.offer(title="Python developer", city="Geneva", country="CH", contract="permanent",
                   remote="hybrid", salary_min=6000, salary_max=8000, salary_period="month")
        self.offer(title="Java developer", city="Lausanne", country="CH", contract="student",
                   remote="on_site", salary_min=90000, salary_period="year")
        self.offer(title="Data analyst", city="Lyon", country="FR", contract="internship",
                   salary_min=3000, salary_max=4000, salary_period="month", currency="EUR")

        def titles(query):
            return sorted(o["title"] for o in Client().get("/api/offers/" + query).json()["results"])

        self.assertEqual(titles("?title=developer"), ["Java developer", "Python developer"])
        self.assertEqual(titles("?title=PYTHON"), ["Python developer"])
        self.assertEqual(titles("?city=lau"), ["Java developer"])
        self.assertEqual(titles("?country=fr"), ["Data analyst"])
        self.assertEqual(titles("?contract=internship"), ["Data analyst"])
        self.assertEqual(titles("?remote=hybrid"), ["Python developer"])
        # A salary filter compares offers of the same period and currency only
        self.assertEqual(titles("?salary_min=7000"), ["Python developer"])
        self.assertEqual(titles("?salary_min=9000"), [])
        self.assertEqual(titles("?salary_min=80000&salary_period=year"), ["Java developer"])
        # In francs unless said otherwise: the offer in euros is left out
        self.assertEqual(titles("?salary_min=3500"), ["Python developer"])
        self.assertEqual(titles("?salary_min=3500&currency=eur"), ["Data analyst"])
        # Published after a date; a bad parameter is ignored
        self.assertEqual(len(titles("?published_after=2000-01-01")), 3)
        self.assertEqual(titles("?published_after=2999-01-01"), [])
        self.assertEqual(len(titles("?published_after=yesterday&salary_min=abc")), 3)

    def test_the_list_is_paged(self):
        for i in range(12):
            self.offer(title="Offer %d" % i)
        data = Client().get("/api/offers/").json()
        self.assertEqual((data["count"], len(data["results"])), (12, 10))
        self.assertIsNotNone(data["next"])
        data = Client().get("/api/offers/?page=2").json()
        self.assertEqual((len(data["results"]), data["next"]), (2, None))
        data = Client().get("/api/offers/?page_size=5").json()
        self.assertEqual(len(data["results"]), 5)
        # Never more than fifty, whatever is asked
        data = Client().get("/api/offers/?page_size=500").json()
        self.assertEqual(len(data["results"]), 12)

    def test_the_detail_is_public_when_published_else_the_employers_only(self):
        published = self.offer(title="Published")
        draft = self.offer(title="Draft", status="draft")
        self.assertEqual(Client().get("/api/offers/%d/" % published.pk).status_code, 200)
        self.assertEqual(Client().get("/api/offers/%d/" % draft.pk).status_code, 404)
        self.assertEqual(self.login(self.candidate).get("/api/offers/%d/" % draft.pk).status_code, 404)
        self.assertEqual(self.login(self.other).get("/api/offers/%d/" % draft.pk).status_code, 404)
        self.assertEqual(self.login(self.employer).get("/api/offers/%d/" % draft.pk).status_code, 200)
        self.assertEqual(Client().get("/api/offers/999/").status_code, 404)

    # ── The management, for an employer ───────────────────────────────

    def test_an_employer_creates_a_draft_and_nobody_else_creates(self):
        employer = self.login(self.employer)
        data = {**OFFER, "salary_min": 6000, "currency": "EUR", "workload_min": 80, "workload_max": 100}
        response = self.post(employer, "/api/offers/", data)
        self.assertEqual(response.status_code, 201)
        offer = response.json()
        self.assertEqual(offer["status"], "draft")
        self.assertEqual((offer["published_at"], offer["company"]["name"]), (None, "Acme"))
        self.assertEqual((offer["remote"], offer["salary_period"], offer["salary_max"]), ("on_site", "month", None))
        self.assertEqual(offer["currency"], "EUR")
        self.assertEqual(JobOffer.objects.get().employer, self.company)
        # A candidate and a visitor may not; the role, not the session, decides
        self.assertEqual(self.post(self.login(self.candidate), "/api/offers/", OFFER).status_code, 403)
        visitor = Client().post("/api/offers/", json.dumps(OFFER), content_type="application/json")
        self.assertEqual(visitor.status_code, 403)

    def test_the_rules_of_the_fields_are_enforced(self):
        employer = self.login(self.employer)

        def errors(**fields):
            response = self.post(employer, "/api/offers/", {**OFFER, **fields})
            self.assertEqual(response.status_code, 400)
            return response.json()

        self.assertIn("title", errors(title=""))
        self.assertIn("country", errors(country="XX"))
        self.assertIn("contract", errors(contract="freelance"))
        self.assertIn("currency", errors(currency="USD"))
        self.assertIn("salary_max", errors(salary_min=8000, salary_max=6000))
        self.assertIn("workload_max", errors(workload_min=100, workload_max=80))
        self.assertIn("workload_min", errors(workload_min=5))
        self.assertIn("experience_years", errors(experience_years=-1))

    def test_the_same_title_may_be_used_twice(self):
        # The same job in two cities, by one employer; and by another one
        employer = self.login(self.employer)
        first = self.post(employer, "/api/offers/", OFFER)
        second = self.post(employer, "/api/offers/", {**OFFER, "city": "Lausanne"})
        self.assertEqual((first.status_code, second.status_code), (201, 201))
        self.assertEqual(self.post(self.login(self.other), "/api/offers/", OFFER).status_code, 201)
        for offer in (first, second):
            self.assertEqual(self.post(employer, "/api/offers/%d/publish/" % offer.json()["id"]).status_code, 200)
        self.assertEqual(Client().get("/api/offers/?title=python").json()["count"], 2)

    def test_an_employer_changes_and_deletes_their_own_offers_only(self):
        mine = self.offer(title="Mine")
        theirs = self.offer(employer=self.other_company, title="Theirs")
        employer = self.login(self.employer)
        response = self.patch(employer, "/api/offers/%d/" % mine.pk, {"city": "Lausanne", "status": "closed"})
        self.assertEqual(response.status_code, 200)
        # The city changed; the status is read only here, it moves by its routes
        self.assertEqual((response.json()["city"], response.json()["status"]), ("Lausanne", "published"))
        self.assertEqual(self.patch(employer, "/api/offers/%d/" % theirs.pk, {"city": "x"}).status_code, 404)
        candidate = self.login(self.candidate)
        self.assertEqual(self.patch(candidate, "/api/offers/%d/" % mine.pk, {"city": "x"}).status_code, 403)
        # PUT is not offered: PATCH is the only way to change
        put = employer.put("/api/offers/%d/" % mine.pk, "{}", content_type="application/json")
        self.assertEqual(put.status_code, 405)
        self.assertEqual(employer.delete("/api/offers/%d/" % theirs.pk).status_code, 404)
        self.assertEqual(employer.delete("/api/offers/%d/" % mine.pk).status_code, 204)
        self.assertFalse(JobOffer.objects.filter(pk=mine.pk).exists())
        self.assertTrue(JobOffer.objects.filter(pk=theirs.pk).exists())

    def test_mine_lists_every_offer_of_the_employer_in_any_state(self):
        self.offer(title="Draft", status="draft")
        self.offer(title="Published")
        self.offer(title="Closed", status="closed")
        self.offer(employer=self.other_company, title="Theirs")
        response = self.login(self.employer).get("/api/offers/mine/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(sorted(o["title"] for o in response.json()), ["Closed", "Draft", "Published"])
        self.assertEqual(self.login(self.candidate).get("/api/offers/mine/").status_code, 403)
        self.assertEqual(Client().get("/api/offers/mine/").status_code, 403)

    def test_an_offer_is_published_closed_and_published_again(self):
        employer = self.login(self.employer)
        offer = self.offer(status="draft")
        url = "/api/offers/%d/" % offer.pk
        # Draft -> published, with its date; the public list sees it now
        response = self.post(employer, url + "publish/")
        self.assertEqual((response.status_code, response.json()["status"]), (200, "published"))
        first = response.json()["published_at"]
        self.assertIsNotNone(first)
        self.assertEqual(Client().get("/api/offers/").json()["count"], 1)
        # Twice: refused
        self.assertEqual(self.post(employer, url + "publish/").status_code, 400)
        # Published -> closed: out of the public list, still readable by its employer
        response = self.post(employer, url + "close/")
        self.assertEqual((response.status_code, response.json()["status"]), (200, "closed"))
        self.assertEqual(Client().get("/api/offers/").json()["count"], 0)
        self.assertEqual(Client().get(url).status_code, 404)
        self.assertEqual(employer.get(url).status_code, 200)
        self.assertEqual(self.post(employer, url + "close/").status_code, 400)
        # Closed -> published again, with a new date
        response = self.post(employer, url + "publish/")
        self.assertEqual(response.status_code, 200)
        self.assertGreater(response.json()["published_at"], first)
        # Somebody else's offer, a candidate, a visitor: no
        theirs = self.offer(employer=self.other_company, status="draft")
        self.assertEqual(self.post(employer, "/api/offers/%d/publish/" % theirs.pk).status_code, 404)
        self.assertEqual(self.post(self.login(self.candidate), url + "close/").status_code, 403)
        self.assertEqual(Client().post(url + "close/").status_code, 403)

    def test_publishing_needs_the_name_of_the_company(self):
        self.company.company_name = ""
        self.company.save()
        employer = self.login(self.employer)
        offer = self.offer(status="draft")
        response = self.post(employer, "/api/offers/%d/publish/" % offer.pk)
        self.assertEqual(response.status_code, 400)
        self.assertIn("company", response.json()["non_field_errors"][0])
        self.assertEqual(JobOffer.objects.get(pk=offer.pk).status, "draft")
        self.company.company_name = "Acme"
        self.company.save()
        self.assertEqual(self.post(employer, "/api/offers/%d/publish/" % offer.pk).status_code, 200)

