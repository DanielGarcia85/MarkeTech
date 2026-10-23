# backend/reviews/urls.py

"""
Reviews URL table — the routes of the reviews API
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Map the routes of the reviews API to their views: the list, public, and
the review of the user. Included by config/urls.py under the prefix api/,
after the appointments. Contains no logic.
"""

from django.urls import path

from .views import MyReviewView, ReviewListView

urlpatterns = [
    path("reviews/", ReviewListView.as_view(), name="review-list"),
    path("reviews/mine/", MyReviewView.as_view(), name="my-review"),
]
