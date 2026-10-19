# backend/profiles/migrations/0002_country_codes.py
#
# The three country fields become ISO 3166-1 codes (CH, FR, ...) instead of
# free text. Written by hand from the output of makemigrations: a data step
# first empties any value that is not a two-letter code (free text typed
# before this change), so that the shrink to two characters never fails on
# PostgreSQL; the three AlterField then narrow the columns.

import django_countries.fields
from django.db import migrations


def clear_free_text(apps, schema_editor):
    """Empty the country values that are not two-letter codes."""
    CandidateProfile = apps.get_model("profiles", "CandidateProfile")
    EmployerProfile = apps.get_model("profiles", "EmployerProfile")
    code = r"^[A-Z]{2}$"
    CandidateProfile.objects.exclude(country__regex=code).update(country="")
    EmployerProfile.objects.exclude(country__regex=code).update(country="")
    EmployerProfile.objects.exclude(company_country__regex=code).update(company_country="")


class Migration(migrations.Migration):

    dependencies = [
        ("profiles", "0001_initial"),
    ]

    operations = [
        # Nothing to undo: the free text is gone for good
        migrations.RunPython(clear_free_text, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="candidateprofile",
            name="country",
            field=django_countries.fields.CountryField(blank=True, max_length=2),
        ),
        migrations.AlterField(
            model_name="employerprofile",
            name="company_country",
            field=django_countries.fields.CountryField(blank=True, max_length=2),
        ),
        migrations.AlterField(
            model_name="employerprofile",
            name="country",
            field=django_countries.fields.CountryField(blank=True, max_length=2),
        ),
    ]
