from django.core.management.base import BaseCommand
from django.db import connections, transaction

from apps.catalog.models import Category

ALLOWED_ROOT_ID = "fe5547de-3d84-11df-96f8-000c6ea69372"


def collect_descendants(category, collected):
    children = Category.objects.using("catalog").filter(parent=category)
    for child in children:
        if str(child.id) not in collected:
            collected.add(str(child.id))
            collect_descendants(child, collected)


class Command(BaseCommand):
    help = "Delete all categories NOT belonging to allowed root tree"

    def handle(self, *args, **options):

        try:
            root = Category.objects.using("catalog").get(id=ALLOWED_ROOT_ID)
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR("Allowed root not found"))
            return

        allowed_ids = set()
        collect_descendants(root, allowed_ids)
        allowed_ids.add(str(root.id))

        self.stdout.write(f"Allowed tree size: {len(allowed_ids)}")

        cursor = connections["catalog"].cursor()

        with transaction.atomic(using="catalog"):

            # удалить property values
            cursor.execute(f"""
                DELETE FROM catalog_propertyvalue
                WHERE product_id IN (
                    SELECT id FROM catalog_product
                    WHERE category_id NOT IN ({",".join(f"'{i}'" for i in allowed_ids)})
                )
            """)

            # удалить продукты
            cursor.execute(f"""
                DELETE FROM catalog_product
                WHERE category_id NOT IN ({",".join(f"'{i}'" for i in allowed_ids)})
            """)

            # удалить категории
            cursor.execute(f"""
                DELETE FROM catalog_category
                WHERE id NOT IN ({",".join(f"'{i}'" for i in allowed_ids)})
            """)

        self.stdout.write(self.style.SUCCESS("Cleanup completed successfully"))
