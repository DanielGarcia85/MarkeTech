# backend/accounts/forms.py

"""
Account forms — extra fields of the sign-up form
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Add the names and the role to the sign-up form of django-allauth, which only
knows the e-mail address and the password. Contains no other form.
"""

from django import forms

from .models import User


class SignupForm(forms.Form):
    """Fields added to allauth's sign-up form, and how they are saved."""

    # Same length as the fields of the user model
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)

    # An administrator is never created through sign-up: only the two roles
    role = forms.ChoiceField(choices=User.Role.choices)

    def signup(self, request, user):
        """Store the names and the role on the user allauth has just created."""
        # Called by allauth once the user is saved; the name is imposed
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.role = self.cleaned_data["role"]
        user.save(update_fields=["first_name", "last_name", "role"])
