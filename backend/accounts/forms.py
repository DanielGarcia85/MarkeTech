# backend/accounts/forms.py

"""
Account forms — extra fields of the sign-up form
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Add the role to the sign-up form of django-allauth, which only knows the
e-mail address and the password. Contains no other form.
"""

from django import forms

from .models import User


class SignupForm(forms.Form):
    """Fields added to allauth's sign-up form, and how they are saved."""

    # An administrator is never created through sign-up: only the two roles
    role = forms.ChoiceField(choices=User.Role.choices)

    def signup(self, request, user):
        """Store the chosen role on the user allauth has just created."""
        # Called by allauth once the user is saved; the name is imposed
        user.role = self.cleaned_data["role"]
        user.save(update_fields=["role"])
