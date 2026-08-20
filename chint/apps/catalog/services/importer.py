import json
import time
from pathlib import Path

from django.conf import settings
from django.db import connections, transaction

from api_test2.services.chint_api import get
from apps.catalog.models import Category, Product, Property, PropertyValue

PROGRESS_FILE = Path(settings.BASE_DIR) / "catalog_import_progress.json"


def api_get(path, params=None, retries=6, sleep=2):
    last = None
    for attempt in range(1, retries + 1):
        resp = get(path, params or {})
        last = resp

        # нормальный ответ
        if isinstance(resp, dict) and resp.get("success") is True and "data" in resp:
            return resp

        # если API вернул ошибку — подождём и повторим
        time.sleep(sleep * attempt)

    raise RuntimeError(
        f"API bad response after retries. path={path} params={params} resp={last}"
    )


def load_progress():
    if PROGRESS_FILE.exists():
        try:
            return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_progress(data: dict):
    PROGRESS_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def import_categories():
    from api_test2.services.catalog_tree import build_tree, collect_descendants

    resp = api_get("/api/product_groups/")
    groups = resp["data"]["product_groups"]

    ROOT_ALLOWED_ID = "fe5547de-3d84-11df-96f8-000c6ea69372"

    nodes, _ = build_tree(groups)

    if ROOT_ALLOWED_ID not in nodes:
        raise RuntimeError("Allowed root not found in API response")

    allowed_ids = collect_descendants(ROOT_ALLOWED_ID, nodes)

    # 1️⃣ создаём/обновляем все категории без parent (НЕ удаляем таблицу!)
    for cid in allowed_ids:
        cid = str(cid)
        g = nodes[cid]
        Category.objects.using("catalog").get_or_create(
            id=g["id"],
            defaults={
                "name": g["name"],
                "parent": None,
            },
        )
    # 2️⃣ проставляем parent (только по allowed_ids)
    category_map = {
        str(c.id): c
        for c in Category.objects.using("catalog").filter(id__in=list(allowed_ids))
    }
    for cid in allowed_ids:
        cid = str(cid)
        g = nodes[cid]
        parent_id = g.get("parent_id")

        if parent_id and parent_id in category_map and cid in category_map:
            cat = category_map[cid]
            if cat.parent_id is None:
                cat.parent = category_map[parent_id]
                cat.save(using="catalog", update_fields=["parent"])

    print(f"✅ Imported {len(allowed_ids)} working categories only")
def import_properties():
    props = api_get("/api/product_properties/")["data"]["properties"]
    for p in props:
        Property.objects.using("catalog").get_or_create(
            id=p["id"],
            defaults={
                "name": p["name"],
                "etim": p.get("etim", ""),
            },
        )
def import_products():
    valid_category_ids = set(
        Category.objects.using("catalog").values_list("id", flat=True)
    )
    progress = load_progress()
    page = int(progress.get("page", 1))
    start_page = page
    PAGE_LIMIT = 100
    first_page = api_get(
        "/api/products/",
        {
            "limit": PAGE_LIMIT,
            "page": 1,
        },
    )
    total_pages = int(first_page["data"]["pages"])
    started_at = time.time()
    while page <= total_pages:
        try:
            resp = api_get(
                "/api/products/",
                {
                    "limit": PAGE_LIMIT,
                    "page": page,
                    "properties": "filled",
                },
            )
        except RuntimeError as e:
            print(f"⚠️ Stop import on page {page}: {e}")
            break
        data = resp["data"]
        with transaction.atomic(using="catalog"):
            for p in data.get("products", []):
                cat_candidate = (
                    p.get("parent_id")
                    or p.get("category_id")
                    or p.get("group_id")
                    or p.get("product_group_id")
                )
                category_id = (
                    cat_candidate if cat_candidate in valid_category_ids else None
                )

                product, created = Product.objects.using("catalog").get_or_create(
                    id=p["id"],
                    defaults={
                        "vendor_code": p.get("vendor_code", ""),
                        "name": p.get("name", ""),
                        "full_name": p.get("full_name", ""),
                        "short_name": p.get("short_name", ""),
                        "category_id": category_id,
                        "etim": p.get("etim", "") or "",
                        "status_article": p.get("status_article", "") or "",
                        "picture": p.get("picture") or None,
                        "raw": p,
                    },
                )

                if not created:
                    # товар уже есть — НЕ ТРОГАЕМ его и его свойства
                    continue
                prop_rows = []

                for pv in p.get("properties", []):
                    prop_rows.append(
                        PropertyValue(
                            product_id=p["id"],
                            property_id=pv["property_id"],
                            value=pv.get("value", "") or "",
                            etim_feature=pv.get("etim_feature", "") or "",
                            etim_value=pv.get("etim_value", "") or "",
                            etim_unit=pv.get("etim_unit", "") or "",
                        )
                    )

                if prop_rows:
                    PropertyValue.objects.using("catalog").bulk_create(
                        prop_rows,
                        batch_size=500,
                        ignore_conflicts=True,
                    )

        save_progress({"page": page + 1})

        percent = int((page / total_pages) * 100)
        elapsed = max(1, int(time.time() - started_at))
        pages_done = max(1, page - start_page + 1)
        sec_per_page = elapsed / pages_done
        remaining = int((total_pages - page) * sec_per_page)

        print(
            f"📦 Products import: {percent}% "
            f"({page}/{total_pages}) | elapsed {elapsed}s | ETA ~{remaining}s"
        )

        page += 1

    if page > total_pages and PROGRESS_FILE.exists():
        PROGRESS_FILE.unlink()


def import_all():
    print("📁 Import categories...")
    import_categories()

    print("🧩 Import properties...")
    import_properties()

    print("📦 Import products...")
    import_products()
