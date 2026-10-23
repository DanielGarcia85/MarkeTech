# backend/demo/views.py

"""
Demo views — opening a demo account without its password
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Let any visitor try the site from the buttons of the login page: one route
opens the session of the demo candidate or of the demo employer, accounts
marked is_demo by seed_demo (decisions of 22.10.2026). The demo accounts
have no usable password in production: this route is the only way into
them, and it reaches nothing else.

Route (demo/urls.py, under /api/)
─────────────────────────────────
  POST  demo/login/   {role: "candidate" or "employer", terms: true}: the
                      session is opened on the demo account of that role,
                      200 with its address and role; 400 without the terms
                      accepted (the box of the login page); 404 when there
                      is no such account (a database without the demo, or
                      another role)
"""

from django.contrib.auth import login
from django.http import Http404
from django.utils.translation import gettext as _
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User


class DemoLoginView(APIView):
    """Open the demo account of a role, for anyone."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Trying the demo is using the site: its terms are accepted first,
        # as at sign-up (decision of 22.10.2026). Nothing is recorded: the
        # account is shared, the acceptance belongs to no one in particular
        if request.data.get("terms") is not True:
            message = _("Accept the terms of use to try the demo.")
            raise ValidationError({"terms": [message]})
        role = request.data.get("role")
        account = User.objects.filter(is_demo=True, is_active=True, role=role).first()
        if role not in User.Role.values or account is None:
            raise Http404
        # The session changes hands, as at any login: a visitor already
        # logged in leaves their own account. The backend is named because
        # two are set (settings, AUTHENTICATION_BACKENDS) and no password
        # was checked to choose one
        login(request, account, backend="django.contrib.auth.backends.ModelBackend")
        return Response({"email": account.email, "role": account.role})
