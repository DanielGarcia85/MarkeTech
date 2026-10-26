# backend/reviews/tests.py

"""
Reviews tests — the reviews and their rules
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Check the model of the reviews: newest first; the database refuses a
second review of the same account, a score outside 1 to 5 and an empty
comment; a review goes with its account. Then the API as the pages will
use it: anyone reads the reviews, ten a page, with their summary; the
author shows as first name and initial, with the company of an employer;
a candidate or an employer writes, rewrites and deletes their own review,
once per account; the scores and the comment are checked; an
administrator has no review, a demo account changes nothing; the review
of a blocked account is out of sight.
"""

import json

from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.test import Client, TestCase

from accounts.models import User
from profiles.models import EmployerProfile

from .models import CRITERIA, Review
from .serializers import WriteSerializer

PASSWORD = "Correct-horse-9"


class ReviewModelTests(TestCase):
    """The reviews of the platform."""

    def setUp(self):
        self.candidate = User.objects.create_user(
            email="cand@example.com", password=PASSWORD, role="candidate"
        )
        self.employer = User.objects.create_user(
            email="emp@example.com", password=PASSWORD, role="employer"
        )

    def review(self, user, **fields):
        values = {"rating": 4, **{field: 4 for field in CRITERIA}, "comment": "Clear and quick."}
        return Review.objects.create(user=user, **{**values, **fields})

    def test_the_reviews_read_newest_first(self):
        first = self.review(self.candidate)
        second = self.review(self.employer)
        self.assertEqual(list(Review.objects.all()), [second, first])
        self.assertEqual(self.candidate.review, first)

    def test_one_review_per_account(self):
        self.review(self.candidate)
        # atomic() keeps the test transaction usable after the refusal
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.review(self.candidate)
        self.assertEqual(Review.objects.count(), 1)

    def test_the_database_refuses_a_bad_score_or_an_empty_comment(self):
        for field in ("rating", *CRITERIA):
            for value in (0, 6):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    self.review(self.candidate, **{field: value})
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.review(self.candidate, comment="")
        self.assertEqual(Review.objects.count(), 0)

    def test_a_review_goes_with_its_account(self):
        self.review(self.candidate)
        self.candidate.delete()
        self.assertEqual(Review.objects.count(), 0)


class ReviewApiTests(TestCase):
    """The reviews through the API."""

    url = "/api/reviews/"
    mine = "/api/reviews/mine/"

    def setUp(self):
        cache.clear()
        self.candidate = User.objects.create_user(
            email="cand@example.com",
            password=PASSWORD,
            role="candidate",
            first_name="Léa",
            last_name="martin",
        )
        self.employer = User.objects.create_user(
            email="emp@example.com",
            password=PASSWORD,
            role="employer",
            first_name="Marc",
            last_name="Dubois",
        )
        EmployerProfile.objects.create(user=self.employer, company_name="Acme")

    # ── Helpers ───────────────────────────────────────────────────────

    def login(self, user):
        """A client logged in as the user, with the CSRF token a browser
        would send back (enforced, as in the other API tests)."""
        client = Client(enforce_csrf_checks=True)
        client.force_login(user)
        client.get("/_allauth/browser/v1/auth/session")
        client.defaults["HTTP_X_CSRFTOKEN"] = client.cookies["csrftoken"].value
        return client

    def scores(self, value=4, **fields):
        """What an author sends: every score, and a comment."""
        return {
            "rating": value,
            **{field: value for field in CRITERIA},
            "comment": "Clear and quick.",
            **fields,
        }

    def put(self, client, data):
        return client.put(self.mine, data=json.dumps(data), content_type="application/json")

    def review(self, user, value=4, **fields):
        return Review.objects.create(user=user, **self.scores(value, **fields))

    # ── Reading ───────────────────────────────────────────────────────

    def test_anyone_reads_the_reviews_newest_first_with_their_summary(self):
        self.review(self.candidate, 5)
        self.review(self.employer, 4, rating=3)
        answer = Client().get(self.url)
        self.assertEqual(answer.status_code, 200)
        body = answer.json()
        self.assertEqual(body["count"], 2)
        self.assertEqual([row["rating"] for row in body["results"]], [3, 5])
        summary = body["summary"]
        self.assertEqual(summary["count"], 2)
        self.assertEqual(summary["averages"]["rating"], 4.0)
        self.assertEqual(summary["averages"]["messaging"], 4.5)
        self.assertEqual(summary["ratings"], {"5": 1, "4": 0, "3": 1, "2": 0, "1": 0})
        # Nobody logged in: no review is theirs
        self.assertFalse(any(row["mine"] for row in body["results"]))

    def test_the_author_shows_as_first_name_and_initial(self):
        self.review(self.candidate)
        self.review(self.employer)
        rows = self.login(self.candidate).get(self.url).json()["results"]
        employer, candidate = rows
        self.assertEqual(
            candidate["author"], {"name": "Léa M.", "role": "candidate", "company": None}
        )
        self.assertTrue(candidate["mine"])
        self.assertEqual(
            employer["author"], {"name": "Marc D.", "role": "employer", "company": "Acme"}
        )
        self.assertFalse(employer["mine"])
        # Never the address, never the whole last name
        text = json.dumps(rows)
        self.assertNotIn("example.com", text)
        self.assertNotIn("Dubois", text)

    def test_a_name_or_a_company_missing_shows_as_none(self):
        self.candidate.last_name = ""
        self.candidate.save()
        nameless = User.objects.create_user(
            email="nameless@example.com", password=PASSWORD, role="employer"
        )
        self.review(self.candidate)
        self.review(nameless)
        nameless_row, candidate_row = Client().get(self.url).json()["results"]
        self.assertEqual(candidate_row["author"]["name"], "Léa")
        # No first name, no profile: the page says "A user"
        self.assertEqual(
            nameless_row["author"], {"name": None, "role": "employer", "company": None}
        )

    def test_ten_a_page_and_three_for_the_side_bar(self):
        for number in range(12):
            user = User.objects.create_user(
                email=f"user{number}@example.com", password=PASSWORD, role="candidate"
            )
            self.review(user, 1 + number % 5)
        body = Client().get(self.url).json()
        self.assertEqual((body["count"], len(body["results"])), (12, 10))
        self.assertIsNotNone(body["next"])
        body = Client().get(self.url, {"page_size": 3}).json()
        self.assertEqual(len(body["results"]), 3)
        # The summary covers every review, not the page
        self.assertEqual(body["summary"]["count"], 12)

    def test_no_review_without_a_role_and_no_average_without_reviews(self):
        admin = User.objects.create_superuser(email="admin@example.com", password=PASSWORD)
        self.review(admin)
        body = Client().get(self.url).json()
        self.assertEqual((body["count"], body["results"]), (0, []))
        self.assertEqual(body["summary"]["count"], 0)
        self.assertIsNone(body["summary"]["averages"]["rating"])
        # The administrator has no review to write
        client = self.login(admin)
        self.assertEqual(client.get(self.mine).status_code, 403)
        self.assertEqual(self.put(client, self.scores()).status_code, 403)

    def test_a_blocked_account_takes_its_review_out_of_sight(self):
        self.review(self.candidate, 5)
        self.review(self.employer, 3)
        # Blocked in the admin: out of the list and of the averages
        User.objects.filter(pk=self.candidate.pk).update(is_active=False)
        body = Client().get(self.url).json()
        self.assertEqual([row["rating"] for row in body["results"]], [3])
        self.assertEqual(body["summary"]["count"], 1)
        self.assertEqual(body["summary"]["averages"]["rating"], 3.0)
        # Nothing was deleted: unblocked, the review is back
        User.objects.filter(pk=self.candidate.pk).update(is_active=True)
        self.assertEqual(Client().get(self.url).json()["count"], 2)

    # ── Writing ───────────────────────────────────────────────────────

    def test_an_author_writes_rewrites_and_deletes_their_review(self):
        client = self.login(self.candidate)
        # No review yet: no content, not an error
        self.assertEqual(client.get(self.mine).status_code, 204)
        answer = self.put(client, self.scores(5, comment="  Very clear.  "))
        self.assertEqual(answer.status_code, 201)
        written = answer.json()
        self.assertEqual(written["comment"], "Very clear.")
        self.assertTrue(written["mine"])
        # Rewritten, still one review, the same one
        answer = self.put(client, self.scores(3))
        self.assertEqual(answer.status_code, 200)
        self.assertEqual(answer.json()["id"], written["id"])
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(client.get(self.mine).json()["rating"], 3)
        # Deleted, then nothing left to delete
        self.assertEqual(client.delete(self.mine).status_code, 204)
        self.assertEqual(client.get(self.mine).status_code, 204)
        self.assertEqual(client.delete(self.mine).status_code, 404)

    def test_the_scores_and_the_comment_are_checked(self):
        client = self.login(self.employer)
        for value in (0, 6, "four", None):
            errors = self.put(client, self.scores(rating=value)).json()
            self.assertEqual(errors, {"rating": ["Give a score from 1 to 5."]})
        missing = self.scores()
        del missing["appointments"]
        errors = self.put(client, missing).json()
        self.assertEqual(errors, {"appointments": ["Give a score from 1 to 5."]})
        errors = self.put(client, self.scores(comment="   ")).json()
        self.assertEqual(errors, {"comment": ["Write a few words about the platform."]})
        errors = self.put(client, self.scores(comment="x" * 1001)).json()
        self.assertEqual(errors, {"comment": ["A review has at most 1000 characters."]})
        self.assertEqual(Review.objects.count(), 0)

    def test_the_form_asks_for_every_score_of_the_model(self):
        self.assertEqual(list(WriteSerializer().fields), ["rating", *CRITERIA, "comment"])

    def test_one_must_be_logged_in_to_write(self):
        client = Client()
        self.assertEqual(client.get(self.mine).status_code, 403)
        self.assertEqual(self.put(client, self.scores()).status_code, 403)

    def test_a_demo_account_reads_its_review_and_changes_nothing(self):
        self.candidate.is_demo = True
        self.candidate.save()
        self.review(self.candidate)
        client = self.login(self.candidate)
        self.assertEqual(client.get(self.mine).status_code, 200)
        answer = self.put(client, self.scores(1))
        self.assertEqual(answer.status_code, 403)
        self.assertEqual(answer.json(), {"detail": "A demo account cannot publish a review."})
        self.assertEqual(client.delete(self.mine).status_code, 403)
        self.assertEqual(Review.objects.get().rating, 4)
