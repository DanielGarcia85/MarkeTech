# backend/demo/throttles.py

"""
Demo throttle — how often a demo account may write
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Keep a demo account, open to anyone, from being used to fill the site:
at most 60 writes an hour per demo account, every view of the API counted
together (decisions of 22.10.2026). Reading is never limited, nor is any
other account. Set for every view of DRF in the settings
(DEFAULT_THROTTLE_CLASSES); the rate is DEFAULT_THROTTLE_RATES["demo"].
"""

from rest_framework.permissions import SAFE_METHODS
from rest_framework.throttling import UserRateThrottle


class DemoWriteThrottle(UserRateThrottle):
    """60 writes an hour for a demo account, no limit for the others."""

    scope = "demo"

    def allow_request(self, request, view):
        if request.method in SAFE_METHODS or not getattr(request.user, "is_demo", False):
            return True
        return super().allow_request(request, view)
