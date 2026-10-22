# backend/demo/middleware.py

"""
Demo middleware — what a demo account may not do
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Keep the demo accounts open to everyone: a visitor logged in on one of
them may not change its e-mail address nor its password, which would lock
the next visitors out (decisions of 22.10.2026). Those two changes go
through the API of allauth, which is not ours: they are refused here,
before it, with a 403 in the shape of its own errors. Everything else is
allowed, files included; the pages show the two forms disabled.
"""

from django.http import JsonResponse

# The routes of allauth that change the address or the password; any
# method but GET (reading the addresses stays allowed)
CLOSED = (
    "/_allauth/browser/v1/account/email",
    "/_allauth/browser/v1/account/password/change",
)


class DemoGuardMiddleware:
    """Refuses the changes of address and password to a demo account."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if (
            request.method != "GET"
            and request.path.rstrip("/") in CLOSED
            and getattr(user, "is_demo", False)
        ):
            message = "A demo account cannot change its address nor its password."
            return JsonResponse(
                {"status": 403, "errors": [{"message": message, "code": "demo_account"}]},
                status=403,
            )
        return self.get_response(request)
