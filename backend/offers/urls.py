# backend/offers/urls.py

"""
Offer URL table — the routes of the offers API
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Map the routes of the offers API to the view set, through the router of
DRF, which derives them from the actions of the view set (list, detail,
mine, publish, close). Included by config/urls.py under the prefix api/.
Contains no logic.
"""

from rest_framework.routers import SimpleRouter

from .views import JobOfferViewSet

# SimpleRouter: the routes and nothing else (DefaultRouter would add an
# index page of the API and the .json suffixes, which the site does not use)
router = SimpleRouter()
# offers/ and offers/<pk>/, plus offers/mine/, offers/<pk>/publish/ and
# offers/<pk>/close/ from the actions; basename names the routes (offer-list,
# offer-detail, offer-mine, offer-publish, offer-close)
router.register("offers", JobOfferViewSet, basename="offer")

urlpatterns = router.urls
