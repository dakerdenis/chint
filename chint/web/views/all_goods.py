from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from api.models import Product, ProductGroup

PER_PAGE = 20

def all_goods(request):
    q = (request.GET.get("q") or "").strip()
    page_number = request.GET.get("page") or "1"
    group = (request.GET.get("group") or "").strip()

    qs = Product.objects.all()
    groups = ProductGroup.objects.order_by("name_ru").only("group_id", "name_ru")

    if group:
        qs = qs.filter(parent_id=group)

    if q:
        qs = qs.filter(
            Q(vendor_code__icontains=q) |
            Q(name_short_ru__icontains=q) |
            Q(name_full_ru__icontains=q)
        )

    qs = qs.order_by("vendor_code")

    paginator = Paginator(qs, PER_PAGE)
    page_obj = paginator.get_page(page_number)

    return render(request, "pages/all-goods.html", {
        "page_obj": page_obj,
        "q": q,
        "group": group,
        "groups": groups,
    })
