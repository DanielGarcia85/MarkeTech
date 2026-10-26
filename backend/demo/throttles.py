# backend/demo/throttles.py

"""
Write throttles — how often an account may write
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Keep an account from being used to fill the site, every view of the API
counted together, per account:
- a demo account, open to anyone: 60 writes an hour at most (decisions of
  22.10.2026);
- any other account: 300 writes an hour at most, far above a real use
  (decision of 26.10.2026), against a script that would flood the messages
  or the offers.
Reading is never limited, nor a visitor who is not logged in (logging in
and signing up have the limits of allauth). Set for every view of DRF in
the settings (DEFAULT_THROTTLE_CLASSES); the rates are
DEFAULT_THROTTLE_RATES["demo"] and ["account"]. Beyond, the API answers
429 with the delay, which the forms show as their error.
"""

from rest_framework.permissions import SAFE_METHODS
from rest_framework.throttling import UserRateThrottle


def writes(request):
    """Whether the request writes, from a logged-in account."""
    return request.method not in SAFE_METHODS and request.user.is_authenticated


class DemoWriteThrottle(UserRateThrottle):
    """60 writes an hour for a demo account."""

    scope = "demo"

    def allow_request(self, request, view):
        if not (writes(request) and request.user.is_demo):
            return True
        return super().allow_request(request, view)


class AccountWriteThrottle(UserRateThrottle):
    """300 writes an hour for any other account."""

    scope = "account"

    def allow_request(self, request, view):
        if not writes(request) or request.user.is_demo:
            return True
        return super().allow_request(request, view)
