import hashlib
import json

from django.core.management.base import BaseCommand
from django.db import transaction

from api.chint import chint_get
from api.models import Product

ALLOWED_LIMIT = 100  # максимум у CHINT

def _hash_product(p: dict) -> str:
    # хешируем только нужные нам поля
    payload = {
        "id": p.get("id"),
        "parent_id": p.get("parent_id"),
        "vendor_code": p.get("vendor_code"),
        "full_name": p.get("full_name"),
        "short_name": p.get("short_name"),
        "name": p.get("name"),
        "picture": p.get("picture"),
        "images": p.get("images") or [],
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class Command(BaseCommand):
    help = "Sync products from CHINT API into local DB"

    def add_arguments(self, parser):
        parser.add_argument("--pages", type=int, default=0, help="Limit pages to sync (0 = all)")
        parser.add_argument("--start-page", type=int, default=1)
        parser.add_argument("--limit", type=int, default=ALLOWED_LIMIT, choices=[25,50,100])

    def handle(self, *args, **opts):
        limit = opts["limit"]
        start_page = opts["start_page"]
        max_pages = opts["pages"]  # 0 = all

        page = start_page
        synced = 0
        updated = 0
        skipped = 0

        while True:
            if max_pages and (page - start_page) >= max_pages:
                break

            data = chint_get("/api/products/", params={"limit": str(limit), "page": str(page)})
            if not data.get("success"):
                raise RuntimeError(f"Upstream error on page {page}: {data}")

            d = data["data"]
            products = d.get("products") or []
            pages_total = int(d.get("pages") or 0)

            if not products:
                break

            with transaction.atomic():
                for p in products:
                    chint_id = p.get("id") or ""
                    vendor_code = p.get("vendor_code") or ""
                    if not chint_id or not vendor_code:
                        continue

                    h = _hash_product(p)

                    obj = Product.objects.filter(chint_id=chint_id).only("id", "source_hash").first()
                    if obj and obj.source_hash == h:
                        skipped += 1
                        continue

                    defaults = {
                        "parent_id": p.get("parent_id") or "",
                        "vendor_code": vendor_code,

                        # CHINT отдаёт русские строки -> кладём ТОЛЬКО в RU-поля
                        "name_full_ru": p.get("full_name") or p.get("name") or "",
                        "name_short_ru": p.get("short_name") or "",

                        "picture_url": p.get("picture") or "",
                        "images": p.get("images") or [],
                        "source_hash": h,
                    }

                    Product.objects.update_or_create(chint_id=chint_id, defaults=defaults)
                    updated += 1

            synced += len(products)
            self.stdout.write(self.style.SUCCESS(
                f"page {page}/{pages_total}: got={len(products)} synced_total={synced} updated={updated} skipped={skipped}"
            ))

            if pages_total and page >= pages_total:
                break
            page += 1

        self.stdout.write(self.style.SUCCESS(
            f"DONE: total_seen={synced} updated={updated} skipped={skipped}"
        ))
