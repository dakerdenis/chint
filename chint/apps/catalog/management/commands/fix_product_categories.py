from django.core.management.base import BaseCommand

from apps.catalog.models import Category, Product


class Command(BaseCommand):
    help = "Fix Product.category from Product.raw['parent_id'] (CHINT API group/category id)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Only show how many products would be updated",
        )

    def handle(self, *args, **options):
        using = "catalog"
        dry_run = options["dry_run"]

        category_map = {
            str(c.id): c
            for c in Category.objects.using(using).only("id")
        }

        qs = Product.objects.using(using).only("id", "category_id", "raw")

        fixed = 0
        skipped_no_parent = 0
        skipped_parent_missing = 0

        for p in qs.iterator(chunk_size=2000):
            raw = p.raw or {}
            parent_id = raw.get("parent_id")

            if not parent_id:
                skipped_no_parent += 1
                continue

            parent = category_map.get(str(parent_id))
            if not parent:
                skipped_parent_missing += 1
                continue

            if p.category_id != parent.id:
                if not dry_run:
                    p.category_id = parent.id
                    p.save(using=using, update_fields=["category"])
                fixed += 1

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN (no changes saved)"))

        self.stdout.write(self.style.SUCCESS(f"✅ Fixed category for {fixed} products"))
        self.stdout.write(f"⏭️ Skipped (no raw.parent_id): {skipped_no_parent}")
        self.stdout.write(f"⏭️ Skipped (parent not found in Category): {skipped_parent_missing}")
