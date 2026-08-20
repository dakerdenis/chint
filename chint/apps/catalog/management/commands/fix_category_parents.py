from django.core.management.base import BaseCommand

from api_test2.services.chint_api import get
from apps.catalog.models import Category


class Command(BaseCommand):
    help = "Fix category parent relations from CHINT API"

    def handle(self, *args, **options):
        resp = get("/api/product_groups/")
        groups = resp["data"]["product_groups"]

        category_map = {
            str(c.id): c
            for c in Category.objects.using("catalog").all()
        }

        fixed = 0

        for g in groups:
            cid = g["id"]
            pid = g.get("parent_id")

            if not pid:
                continue

            cat = category_map.get(cid)
            parent = category_map.get(pid)

            if cat and parent and cat.parent_id != parent.id:
                cat.parent = parent
                cat.save(using="catalog")
                fixed += 1

        self.stdout.write(
            self.style.SUCCESS(f"✅ Fixed parent for {fixed} categories")
        )
