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
from django.urls import path

# Django reads this list, in order, to find the route matching a request
urlpatterns = [
    # Administration interface
    path("admin/", admin.site.urls),
]
