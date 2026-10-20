# backend/applications/urls.py

"""
Application URL table — the routes of the applications API
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Map the routes of the applications API to the view set, through the router
of DRF, which derives them from the actions of the view set (list, detail,
status, cv, cover-letter, attachments). Included by config/urls.py under
the prefix api/. Contains no logic.
"""

from rest_framework.routers import SimpleRouter

from .views import JobApplicationViewSet

# SimpleRouter: the routes and nothing else, like the offers
router = SimpleRouter()
# applications/ and applications/<pk>/, plus applications/<pk>/status/,
# applications/<pk>/cv/, applications/<pk>/cover-letter/ and
# applications/<pk>/attachments/<id>/ from the actions; basename names the
# routes (application-list, application-detail, application-change-status,
# application-cv, application-cover-letter, application-attachment)
router.register("applications", JobApplicationViewSet, basename="application")

urlpatterns = router.urls
