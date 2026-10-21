# backend/favorites/urls.py

"""
Favorite URL table — the routes of the favorites API
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Map the routes of the favorites API to the view set, through the router of
DRF, which derives them from the actions of the view set (list, create,
destroy). Included by config/urls.py under the prefix api/. Contains no
logic.
"""

from rest_framework.routers import SimpleRouter

from .views import FavoriteViewSet

# SimpleRouter: the routes and nothing else, like the offers
router = SimpleRouter()
# favorites/ and favorites/<offer id>/; basename names the routes
# (favorite-list, favorite-detail)
router.register("favorites", FavoriteViewSet, basename="favorite")

urlpatterns = router.urls
