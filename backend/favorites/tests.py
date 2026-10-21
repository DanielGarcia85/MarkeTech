# backend/favorites/tests.py

"""
Favorite tests — the favorites and their API
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Check the favorites as the frontend will use them: a candidate puts a
published offer aside once, lists their favorites with the offers as the
cards show them, takes one back by the offer; every offer tells a
candidate whether it is among their favorites, and nobody else; a visitor
and an employer are kept out; the employer of an offer is told how many
candidates put it aside, nobody else.
"""

import json

from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.test import Client, TestCase

from accounts.models import User
from offers.models import JobOffer
from profiles.models import CandidateProfile, EmployerProfile

from .models import Favorite

PASSWORD = "Correct-horse-9"

# What a valid new offer needs
OFFER = {
    "title": "Python developer",
    "description": "Django and Vue.",
    "city": "Geneva",
    "country": "CH",
    "contract": "permanent",
}


class FavoriteApiTests(TestCase):
    """Putting aside, listing, taking back; the flag and the count."""

    def setUp(self):
        cache.clear()
        self.candidate = User.objects.create_user(
            email="cand@example.com", password=PASSWORD, role="candidate"
        )
        self.other_candidate = User.objects.create_user(
            email="cand2@example.com", password=PASSWORD, role="candidate"
        )
        self.employer = User.objects.create_user(
            email="emp@example.com", password=PASSWORD, role="employer"
        )
        self.profile = CandidateProfile.objects.create(user=self.candidate)
        CandidateProfile.objects.create(user=self.other_candidate)
        self.company = EmployerProfile.objects.create(user=self.employer, company_name="Acme")
        self.offer = JobOffer.objects.create(employer=self.company, status="published", **OFFER)
        self.other_offer = JobOffer.objects.create(
            employer=self.company, status="published", title="Vue developer", **{k: v for k, v in OFFER.items() if k != "title"}
        )

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

    # ── The model ─────────────────────────────────────────────────────

    def test_an_offer_is_put_aside_once_and_goes_with_the_offer(self):
        Favorite.objects.create(candidate=self.profile, offer=self.offer)
        # The database refuses the second one; atomic() keeps the test
        # transaction usable after the error
        with self.assertRaises(IntegrityError), transaction.atomic():
            Favorite.objects.create(candidate=self.profile, offer=self.offer)
        self.offer.delete()
        self.assertEqual(Favorite.objects.count(), 0)

    # ── Putting aside, listing, taking back ───────────────────────────

    def test_a_candidate_puts_an_offer_aside_and_lists_it(self):
        client = self.login(self.candidate)
        response = self.post(client, "/api/favorites/", {"offer": self.offer.pk})
        self.assertEqual(response.status_code, 201, response.content)
        data = response.json()
        # The offer as the cards show it, with the heart on
        self.assertEqual(data["offer"]["title"], "Python developer")
        self.assertEqual(data["offer"]["company"], {"name": "Acme", "logo": None})
        self.assertTrue(data["offer"]["favorite"])
        self.assertEqual(self.post(client, "/api/favorites/", {"offer": self.other_offer.pk}).status_code, 201)
        response = client.get("/api/favorites/")
        self.assertEqual(response.status_code, 200)
        # Newest first, each with its offer
        self.assertEqual([f["offer"]["title"] for f in response.json()], ["Vue developer", "Python developer"])
        # Someone else's favorites are not listed
        Favorite.objects.create(candidate=CandidateProfile.objects.get(user=self.other_candidate), offer=self.offer)
        self.assertEqual(len(client.get("/api/favorites/").json()), 2)

    def test_putting_aside_is_refused_twice_and_outside_the_published_offers(self):
        client = self.login(self.candidate)
        self.assertEqual(self.post(client, "/api/favorites/", {"offer": self.offer.pk}).status_code, 201)
        response = self.post(client, "/api/favorites/", {"offer": self.offer.pk})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"offer": ["This offer is already in your favourites."]})
        for status in ("draft", "closed"):
            offer = JobOffer.objects.create(employer=self.company, status=status, **OFFER)
            response = self.post(client, "/api/favorites/", {"offer": offer.pk})
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {"offer": ["This offer cannot be put aside."]})
        response = self.post(client, "/api/favorites/", {"offer": 9999})
        self.assertEqual(response.json(), {"offer": ["This offer cannot be put aside."]})
        self.assertEqual(Favorite.objects.count(), 1)

    def test_a_favorite_stays_when_the_offer_is_closed(self):
        client = self.login(self.candidate)
        self.post(client, "/api/favorites/", {"offer": self.offer.pk})
        self.offer.status = "closed"
        self.offer.save()
        favorites = client.get("/api/favorites/").json()
        self.assertEqual([f["offer"]["status"] for f in favorites], ["closed"])

    def test_a_candidate_takes_an_offer_back_by_its_id(self):
        client = self.login(self.candidate)
        self.post(client, "/api/favorites/", {"offer": self.offer.pk})
        # Keyed by the offer, not by the favorite
        response = client.delete("/api/favorites/%d/" % self.offer.pk)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Favorite.objects.count(), 0)
        self.assertEqual(client.delete("/api/favorites/%d/" % self.offer.pk).status_code, 404)
        # Someone else's favorite: not found either
        Favorite.objects.create(candidate=CandidateProfile.objects.get(user=self.other_candidate), offer=self.offer)
        self.assertEqual(client.delete("/api/favorites/%d/" % self.offer.pk).status_code, 404)
        self.assertEqual(Favorite.objects.count(), 1)

    def test_only_a_candidate_has_favorites(self):
        employer = self.login(self.employer)
        self.assertEqual(employer.get("/api/favorites/").status_code, 403)
        self.assertEqual(self.post(employer, "/api/favorites/", {"offer": self.offer.pk}).status_code, 403)
        self.assertEqual(employer.delete("/api/favorites/%d/" % self.offer.pk).status_code, 403)
        self.assertEqual(Client().get("/api/favorites/").status_code, 403)

    # ── The flag on the offers, the count for the employer ────────────

    def test_every_offer_tells_a_candidate_whether_it_is_a_favorite(self):
        Favorite.objects.create(candidate=self.profile, offer=self.offer)
        client = self.login(self.candidate)
        flags = {o["title"]: o["favorite"] for o in client.get("/api/offers/").json()["results"]}
        self.assertEqual(flags, {"Python developer": True, "Vue developer": False})
        self.assertTrue(client.get("/api/offers/%d/" % self.offer.pk).json()["favorite"])
        # Another candidate, a visitor, the employer: never
        for other in (self.login(self.other_candidate), Client(), self.login(self.employer)):
            self.assertFalse(other.get("/api/offers/%d/" % self.offer.pk).json()["favorite"])
            flags = [o["favorite"] for o in other.get("/api/offers/").json()["results"]]
            self.assertEqual(flags, [False, False])

    def test_the_employer_is_told_how_many_put_the_offer_aside(self):
        Favorite.objects.create(candidate=self.profile, offer=self.offer)
        Favorite.objects.create(candidate=CandidateProfile.objects.get(user=self.other_candidate), offer=self.offer)
        client = self.login(self.employer)
        counts = {o["id"]: o["favorites_count"] for o in client.get("/api/offers/mine/").json()}
        self.assertEqual(counts, {self.offer.pk: 2, self.other_offer.pk: 0})
        self.assertEqual(client.get("/api/offers/%d/" % self.offer.pk).json()["favorites_count"], 2)
        # Not for the public, nor for a candidate
        for other in (Client(), self.login(self.candidate)):
            self.assertNotIn("favorites_count", other.get("/api/offers/%d/" % self.offer.pk).json())
