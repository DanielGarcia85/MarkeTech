import os
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Install requirements, runs migrate and loads fixtures automatically'

    def handle(self, *args, **kwargs):

        self.stdout.write(self.style.MIGRATE_HEADING("=== Initial Setup Starting ==="))

        self.stdout.write(self.style.WARNING("=> Cleaning media folder..."))
        self.clean_media_folders()
        self.stdout.write(self.style.SUCCESS("=> Media folder cleaned"))

        if os.path.exists("db.sqlite3"):
            self.stdout.write(self.style.WARNING("=> Deleting database db.sqlite3..."))
            os.remove("db.sqlite3")
            self.stdout.write(self.style.SUCCESS("=> Database deleted"))
        else:
            self.stdout.write(self.style.NOTICE("=> No database found to delete."))

        self.stdout.write(self.style.WARNING("=> Running migrations..."))
        call_command("makemigrations")
        call_command("migrate")
        self.stdout.write(self.style.SUCCESS("=> Migrations completed"))
    

        self.stdout.write(self.style.WARNING("=> Loading fixtures..."))
        fixtures = [
            "users.json",
            "user_groups.json",
            "employers.json",
            "jobseekers.json",
            "jobposts.json",
            "jobapplications.json",
            "system_reviews.json",
            "jobapplications.json",
        ]
        for fixture in fixtures:
            try:
                call_command("loaddata", f"backend/api/fixtures/{fixture}")
                self.stdout.write(self.style.SUCCESS(f"Loaded {fixture}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to load {fixture}: {e}"))
                import traceback
                traceback.print_exc()
        self.stdout.write(self.style.SUCCESS("=> Fixtures loaded"))
        self.stdout.write(self.style.MIGRATE_HEADING("=== Initial Setup Successfully Completed ==="))
                
    def clean_media_folders(self):
        """Deletes all files in the media/ sub-folders except those containing 'place_holder'"""
        base_folder = "media"
        if os.path.exists(base_folder):
            for root, dirs, files in os.walk(base_folder):
                for filename in files:
                    if "place_holder" not in filename and not filename.startswith("fixture_"):  # Ignore files containing 'place_holder' and those starting with 'fixture_'
                        file_path = os.path.join(root, filename)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                            self.stdout.write(f"Deleted: {file_path}")