# backend/reviews/tests.py

"""
Reviews tests — the reviews and their rules
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Check the model of the reviews: newest first; the database refuses a
second review of the same account, a score outside 1 to 5 and an empty
comment; a review goes with its account.
"""

from django.db import IntegrityError, transaction
from django.test import TestCase

from accounts.models import User

from .models import CRITERIA, Review

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
