# backend/accounts/signals.py

"""
Account signals — what the accounts application does when Django says so
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Keep the language of a user: at every login, the language of the request
(chosen by LocaleMiddleware from the Accept-Language header the frontend
sends, the language of the interface) becomes the language of the e-mails
the user will receive without asking for them, the notifications
(decisions of 26.10.2026). The signal of Django, not the one of allauth:
the login of a demo account (demo/views.py) sends it too. Connected by
apps.py when the application is ready.
"""

from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


@receiver(user_logged_in)
def remember_language(sender, request, user, **kwargs):
    """The language of the request becomes that of the user, if it is one
    the site offers; written only when it changes."""
    language = getattr(request, "LANGUAGE_CODE", "")
    if language in dict(settings.LANGUAGES) and user.language != language:
        user.language = language
        user.save(update_fields=["language"])
