from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import health, MessageViewSet

router = DefaultRouter()
router.register(r"messages", MessageViewSet, basename="message")

urlpatterns = [
    path("health/", health, name="health"),
    path("", include(router.urls)),
]
