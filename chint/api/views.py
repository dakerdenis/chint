import hashlib
import json

from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .chint import chint_get

CACHE_TTL = 60 * 5  # 5 минут

@require_GET
def products(request):
    # пробрасываем безопасные query params как есть (можно ужесточить whitelist при желании)
    params = {}
    # 1) простые строковые фильтры — как есть, но без пустых
    for k in ("etim", "properties", "etim_properties", "vendor_code"):
        v = (request.GET.get(k) or "").strip()
        if v:
            params[k] = v

    # 2) limit — у CHINT допустимы только 0,25,50,100 (по их доке)
    limit = (request.GET.get("limit") or "25").strip()
    if limit not in ("0", "25", "50", "100"):
        limit = "25"
    params["limit"] = limit

    # 3) page — только число >= 1
    page = (request.GET.get("page") or "1").strip()
    if not page.isdigit() or int(page) < 1:
        page = "1"
    params["page"] = page

    # кеш ключ на основе params
    raw = json.dumps(params, sort_keys=True, ensure_ascii=False).encode("utf-8")
    cache_key = "chint:products:" + hashlib.md5(raw).hexdigest()


    cached = cache.get(cache_key)
    if cached is not None:
        return JsonResponse(cached, safe=False)

    try:
        data = chint_get("/api/products/", params=params)
    except Exception as e:
        return JsonResponse(
            {"success": False, "error": {"message": "Upstream CHINT API error", "details": str(e)}},
            status=502,
        )

        # --- нормализуем ответ: оставляем только то, что нужно фронту ---
    d = (data or {}).get("data") or {}
    products = d.get("products") or []

    slim_products = []
    for p in products:
        slim_products.append({
            "id": p.get("id"),
            "parent_id": p.get("parent_id"),
            "vendor_code": p.get("vendor_code"),
            "title": p.get("short_name") or p.get("name") or p.get("full_name"),
            "full_title": p.get("full_name") or p.get("name"),
            "picture": p.get("picture"),
            "images": p.get("images") or [],   # если вдруг у них есть
        })

    slim = {
        "success": True,
        "data": {
            "products_count": d.get("products_count"),
            "products_all_count": d.get("products_all_count"),
            "pages": d.get("pages"),
            "current_page": d.get("current_page"),
            "limit": d.get("limit"),
            "products": slim_products,
        }
    }

    cache.set(cache_key, slim, CACHE_TTL)
    return JsonResponse(slim, safe=False)

