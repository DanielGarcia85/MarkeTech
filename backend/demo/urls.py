# backend/demo/urls.py

"""
Demo URL table — the route of the public demonstration
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Map the login to a demo account to its view. Included by config/urls.py
under the prefix api/. Contains no logic.
"""

from django.urls import path

from .views import DemoLoginView

urlpatterns = [
    path("demo/login/", DemoLoginView.as_view(), name="demo-login"),
]
