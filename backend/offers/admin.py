# backend/offers/admin.py

"""
Offers administration — job offers in the Django admin site
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Register the job offers in the administration interface: a list filtered by
state, contract and country, searchable by title and by the company or the
address of the employer. Contains no business logic: the admin site is a
tool for the administrator, not a feature of the site.
"""

from django.contrib import admin

from .models import JobOffer


@admin.register(JobOffer)
class JobOfferAdmin(admin.ModelAdmin):
    """Job offers: list, filters, search, one page per offer."""

    list_display = ("id", "title", "company", "city", "country", "status", "published_at")
    list_display_links = ("id", "title")
    list_filter = ("status", "contract", "remote", "country")
    search_fields = ("title", "employer__company_name", "employer__user__email")
    ordering = ("-created_at",)
    # The employer is chosen by typing part of the company or of the address,
    # not in a list of every profile (search done by EmployerProfileAdmin)
    autocomplete_fields = ("employer",)
    readonly_fields = ("published_at", "created_at", "updated_at")
    # Load the profile and its account with each offer of the list, in a
    # single query: the company column reads them
    list_select_related = ("employer__user",)
    fieldsets = (
        (None, {"fields": ("employer", "title", "description")}),
        ("Place", {"fields": ("city", "country", "remote")}),
        (
            "Conditions",
            {
                "fields": (
                    "contract",
                    ("workload_min", "workload_max"),
                    ("salary_min", "salary_max", "salary_period"),
                    "experience_years",
                ),
            },
        ),
        ("State", {"fields": ("status", "published_at", "created_at", "updated_at")}),
    )

    @admin.display(ordering="employer__company_name", description="company")
    def company(self, offer):
        """Name of the company, as a column of the list."""
        return offer.employer.company_name
