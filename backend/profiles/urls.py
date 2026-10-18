# backend/profiles/urls.py

"""
Profile URL table — the routes of the profiles API
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Map each route of the profiles API to its view. Included by config/urls.py
under the prefix api/. Contains no logic.
"""

from django.urls import path

from . import views

urlpatterns = [
    # The profile of the logged-in user
    path("profile/", views.ProfileView.as_view(), name="profile"),
    # One file of the profile; the third argument names the field for the
    # view, so that each route stays explicit
    path("profile/photo/", views.ProfileFileView.as_view(), {"field": "photo"}, name="profile-photo"),
    path("profile/cv/", views.ProfileFileView.as_view(), {"field": "cv"}, name="profile-cv"),
    path("profile/logo/", views.ProfileFileView.as_view(), {"field": "logo"}, name="profile-logo"),
    # The further documents of a candidate
    path("profile/documents/", views.DocumentListView.as_view(), name="profile-documents"),
    path("profile/documents/<int:pk>/", views.DocumentView.as_view(), name="profile-document"),
    # The files of the users, by their path under MEDIA_ROOT
    path("files/<path:path>", views.FileView.as_view(), name="file"),
]
