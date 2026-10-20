# backend/accounts/forms.py

"""
Account forms — extra fields of the sign-up form
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Add the names, the role and the acceptance of the terms of use to the
sign-up form of django-allauth, which only knows the e-mail address and the
password, and create the empty profile of the chosen role. Contains no other
form.
"""

from django import forms
from django.utils import timezone

from profiles.models import CandidateProfile, EmployerProfile

from .models import User


class SignupForm(forms.Form):
    """Fields added to allauth's sign-up form, and how they are saved."""

    # Same length as the fields of the user model
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)

    # An administrator is never created through sign-up: only the two roles
    role = forms.ChoiceField(choices=User.Role.choices)
    # The terms of use must be accepted: a BooleanField is required by
    # default, so false or missing is refused with "This field is required."
    terms = forms.BooleanField()

    def signup(self, request, user):
        """Store the names, the role and the time of the acceptance of the
        terms on the user allauth has just created, then give the user the
        profile of that role."""
        # Called by allauth once the user is saved; the name is imposed
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.role = self.cleaned_data["role"]
        # The form is only valid with the box ticked: the date is the proof
        user.terms_accepted_at = timezone.now()
        user.save(update_fields=["first_name", "last_name", "role", "terms_accepted_at"])

        # The profile is created empty: the user completes it on the profile
        # page, once the address is verified and the first login done
        if user.role == User.Role.CANDIDATE:
            CandidateProfile.objects.create(user=user)
        else:
            EmployerProfile.objects.create(user=user)
