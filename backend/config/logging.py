# backend/config/logging.py

"""
Logging filters — what the journal of the backend leaves out
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Keep the journal readable. Django writes a warning for every answer in the
4xx range (logger django.request). Two of them are no error: every visit of
a logged-out visitor asks the authentication API whether someone is logged
in, and allauth answers 401 for "nobody"; logging out answers 401 too, by
design. This filter drops these two, and only these: a 401 anywhere else
stays in the journal. Plugged in by LOGGING in settings/base.py.
"""

import logging

# The address of allauth's session, asked at every visit (GET) and used to
# log out (DELETE)
SESSION_PATH = "/_allauth/browser/v1/auth/session"


class SkipAnonymousSession(logging.Filter):
    """Drop the 401 of allauth's session route, the answer for "nobody is
    logged in" (decision of 29.10.2026)."""

    def filter(self, record):
        """False, so not written, for a 401 on the session route."""
        request = getattr(record, "request", None)
        anonymous_session = (
            getattr(record, "status_code", None) == 401
            and request is not None
            and request.path == SESSION_PATH
        )
        return not anonymous_session
