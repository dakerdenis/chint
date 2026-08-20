from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from api.models import Product

@require_GET
def catalog_products(request):
    q = (request.GET.get("q") or "").strip()
    sort = (request.GET.get("sort") or "vendor_code").strip()
    page = int(request.GET.get("page") or 1)
    per_page = min(int(request.GET.get("per_page") or 20), 50)

    qs = Product.objects.all()

    if q:
        qs = qs.filter(
            Q(vendor_code__icontains=q) |
            Q(name_short__icontains=q) |
            Q(name_full__icontains=q)
        )

    if sort == "name":
        qs = qs.order_by("name_short", "vendor_code")
    elif sort == "-name":
        qs = qs.order_by("-name_short", "vendor_code")
    elif sort == "-vendor_code":
        qs = qs.order_by("-vendor_code")
    else:
        qs = qs.order_by("vendor_code")

    total = qs.count()
    offset = (page - 1) * per_page
    items = list(qs[offset:offset + per_page].values(
        "vendor_code", "name_short", "name_full", "picture_url", "images", "parent_id"
    ))

    return JsonResponse({
        "success": True,
        "data": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "items": items,
        }
    })
