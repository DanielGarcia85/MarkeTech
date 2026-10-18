# backend/profiles/admin.py

"""
Profiles administration — profiles and documents in the Django admin site
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Register the two profiles in the administration interface: a list per role,
searchable by the address and the names of the account, and the documents
of a candidate shown on the page of their profile. Contains no business
logic: the admin site is a tool for the administrator, not a feature of the
site.
"""

from django.contrib import admin

from .models import CandidateDocument, CandidateProfile, EmployerProfile

# Block of contact fields, the same on both screens
CONTACT_FIELDSET = (
    "Contact details",
    {"fields": ("phone", "address", "postal_code", "city", "country")},
)


class CandidateDocumentInline(admin.TabularInline):
    """Documents of a candidate, listed on the page of the profile."""

    model = CandidateDocument
    # No empty row offered by default: a document is added on purpose
    extra = 0
    readonly_fields = ("uploaded_at",)


class ProfileAdmin(admin.ModelAdmin):
    """What the two profile screens share: the account and the search."""

    # The account is chosen by typing part of its address or name, not in
    # a list of every account (search done by UserAdmin.search_fields)
    autocomplete_fields = ("user",)
    readonly_fields = ("updated_at",)
    search_fields = ("user__email", "user__first_name", "user__last_name")
    ordering = ("user__email",)
    # Load the account with each profile of the list, in a single query
    list_select_related = ("user",)

    @admin.display(ordering="user__email", description="e-mail")
    def email(self, profile):
        """Address of the account, as a column of the list."""
        return profile.user.email


@admin.register(CandidateProfile)
class CandidateProfileAdmin(ProfileAdmin):
    """Candidate profiles: list, search, and the documents in line."""

    list_display = ("id", "email", "city", "country", "cv", "updated_at")
    list_display_links = ("id", "email")
    fieldsets = (
        (None, {"fields": ("user",)}),
        CONTACT_FIELDSET,
        ("Files", {"fields": ("photo", "cv")}),
        ("Dates", {"fields": ("updated_at",)}),
    )
    inlines = (CandidateDocumentInline,)


@admin.register(EmployerProfile)
class EmployerProfileAdmin(ProfileAdmin):
    """Employer profiles: list by company, search."""

    list_display = ("id", "email", "company_name", "company_city", "updated_at")
    list_display_links = ("id", "email")
    search_fields = ProfileAdmin.search_fields + ("company_name",)
    fieldsets = (
        (None, {"fields": ("user",)}),
        CONTACT_FIELDSET,
        (
            "Company",
            {
                "fields": (
                    "company_name",
                    "company_address",
                    "company_postal_code",
                    "company_city",
                    "company_country",
                    "company_phone",
                    "logo",
                ),
            },
        ),
        ("Dates", {"fields": ("updated_at",)}),
    )
