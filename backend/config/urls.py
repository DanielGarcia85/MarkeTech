# backend/config/urls.py

"""
Root URL table — maps each URL prefix to the code that handles it
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Declare the top-level routes of the backend and delegate each prefix to the
relevant module. Contains no view and no business logic.

Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))

References
──────────
  - https://docs.djangoproject.com/en/6.1/topics/http/urls/
"""

from django.contrib import admin
from django.urls import include, path

from .views import health

# Django reads this list, in order, to find the route matching a request
urlpatterns = [
    # Administration interface
    path("admin/", admin.site.urls),
    # Health check of the backend
    path("api/health/", health, name="health"),
    # Authentication API of allauth (sign-up, login, e-mail verification...)
    path("_allauth/", include("allauth.headless.urls")),
    # Profiles API: the profile of the user, their documents, the files
    path("api/", include("profiles.urls")),
    # Offers API: the job offers, public reading and management by the employers
    path("api/", include("offers.urls")),
    # Applications API: the candidates applying to the offers, both sides reading
    path("api/", include("applications.urls")),
    # Favorites API: the offers a candidate puts aside
    path("api/", include("favorites.urls")),
    # Messaging API: the conversations of the applications in progress
    path("api/", include("messaging.urls")),
    # Demo API: the login to a demo account, for any visitor
    path("api/", include("demo.urls")),
]
