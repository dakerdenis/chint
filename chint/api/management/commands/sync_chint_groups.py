import hashlib
import json
from django.core.management.base import BaseCommand
from django.db import transaction

from api.chint import chint_get
from api.models import ProductGroup


def _hash_group(g: dict) -> str:
    payload = {
        "id": g.get("id"),
        "parent_id": g.get("parent_id"),
        "name": g.get("name"),
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class Command(BaseCommand):
    help = "Sync product groups from CHINT API into local DB"

    def handle(self, *args, **options):
        data = chint_get("/api/product_groups/", params={})
        if not data.get("success"):
            raise RuntimeError(f"Upstream error: {data}")

        d = data.get("data") or {}
        groups = d.get("product_groups") or []

        updated = 0
        skipped = 0

        with transaction.atomic():
            for g in groups:
                gid = (g.get("id") or "").strip()
                if not gid:
                    continue

                h = _hash_group(g)

                obj = ProductGroup.objects.filter(group_id=gid).only("id").first()
                # у нас нет source_hash в модели группы — можно просто update_or_create
                # но чтобы меньше писать в БД, сравним через name/parent_id
                parent_id = (g.get("parent_id") or "").strip()
                name_ru = (g.get("name") or "").strip()

                obj = ProductGroup.objects.filter(group_id=gid).only("id", "source_hash").first()
                if obj and obj.source_hash == h:
                    skipped += 1
                    continue
               

                ProductGroup.objects.update_or_create(
                    group_id=gid,
                    defaults={
                        "parent_id": parent_id,
                        "name_ru": name_ru,
                        "source_hash": h,
                    },
                )
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"DONE: groups_total={len(groups)} updated={updated} skipped={skipped}"
        ))
