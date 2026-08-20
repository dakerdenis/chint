from django.core.management.base import BaseCommand

from apps.catalog.services.importer import import_all


class Command(BaseCommand):
    help = "Import full catalog from CHINT API into local catalog DB"

    def handle(self, *args, **options):
        self.stdout.write("⏳ Import started...")
        import_all()
        self.stdout.write(self.style.SUCCESS("✅ Import finished successfully"))
