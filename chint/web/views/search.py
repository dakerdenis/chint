from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator

from apps.catalog.models import Product, PropertyValue
from web.views.catalog_products import (
    PER_PAGE,
    EXCLUDED_PROPERTY_IDS,
    PRIORITY_PROPERTY_IDS,
)


def search(request):
    """Просто рендерит страницу. Всё остальное грузится через AJAX."""
    query = request.GET.get("q", "").strip()
    return render(request, "pages/search.html", {
        "query": query,
    })


def search_products(request):
    """JSON API: товары + фасеты по поисковому запросу."""
    query = request.GET.get("q", "").strip()
    page = int(request.GET.get("page", 1))
    lang = request.LANGUAGE_CODE

    if not query:
        return JsonResponse({
            "count": 0,
            "page": 1,
            "num_pages": 0,
            "results": [],
            "facets": {},
            "query": "",
        })

    base_filters = (
        Q(vendor_code__icontains=query) |
        Q(name__icontains=query) |
        Q(short_name__icontains=query) |
        Q(name_en__icontains=query) |
        Q(name_az__icontains=query) |
        Q(name_ka__icontains=query) |
        Q(short_name_en__icontains=query) |
        Q(short_name_az__icontains=query) |
        Q(short_name_ka__icontains=query)
    )

    products_qs = (
        Product.objects.using("catalog")
        .filter(base_filters)
        .exclude(category__isnull=True)
    )

    # ---------- ФИЛЬТРЫ ПО СВОЙСТВАМ ----------
    filters = {}
    for key, values in request.GET.lists():
        if key.startswith("prop_"):
            prop_id = key.replace("prop_", "")
            filters[prop_id] = values

    for prop_id, values in filters.items():
        products_qs = products_qs.filter(
            properties__property_id=prop_id,
            properties__value__in=values,
        )

    products_qs = products_qs.distinct().order_by("vendor_code")

    paginator = Paginator(products_qs, PER_PAGE)
    page_obj = paginator.get_page(page)

    # ---------- ФАСЕТЫ ----------
    # ID найденных товаров (по базовому поиску, без учёта выбранных фасетов —
    # иначе фасеты "схлопнутся" и нельзя будет выбрать другие значения).
    matched_ids = list(
        Product.objects.using("catalog")
        .filter(base_filters)
        .values_list("id", flat=True)
    )

    facets_qs = (
        PropertyValue.objects.using("catalog")
        .select_related("property")
        .filter(product_id__in=matched_ids)
        .exclude(product__category__isnull=True)
        .exclude(property_id__in=EXCLUDED_PROPERTY_IDS)
        .values(
            "property_id",
            "property__name",
            "property__name_en",
            "property__name_az",
            "property__name_ka",
            "value",
            "value_en",
            "value_az",
            "value_ka",
        )
        .annotate(count=Count("product", distinct=True))
        .order_by("property__name", "value")
    )

    facets = {}
    for f in facets_qs:
        pid = str(f["property_id"])

        if lang == "en" and f["property__name_en"]:
            prop_name = f["property__name_en"]
        elif lang == "az" and f["property__name_az"]:
            prop_name = f["property__name_az"]
        elif lang == "ka" and f["property__name_ka"]:
            prop_name = f["property__name_ka"]
        else:
            prop_name = f["property__name"]

        facets.setdefault(pid, {"name": prop_name, "values": []})

        if lang == "en" and f["value_en"]:
            value_label = f["value_en"]
        elif lang == "az" and f["value_az"]:
            value_label = f["value_az"]
        elif lang == "ka" and f["value_ka"]:
            value_label = f["value_ka"]
        else:
            value_label = f["value"]

        facets[pid]["values"].append({
            "value": value_label,
            "count": f["count"],
        })

    priority_map = {pid: i for i, pid in enumerate(PRIORITY_PROPERTY_IDS)}
    sorted_facets = dict(
        sorted(facets.items(), key=lambda x: priority_map.get(x[0], 9999))
    )

    return JsonResponse({
        "count": paginator.count,
        "page": page_obj.number,
        "num_pages": paginator.num_pages,
        "query": query,
        "results": [
            {
                "id": str(p.id),
                "name": (
                    p.short_name_en if lang == "en" and p.short_name_en else
                    p.short_name_az if lang == "az" and p.short_name_az else
                    p.short_name_ka if lang == "ka" and p.short_name_ka else
                    p.short_name or p.name
                ),
                "vendor_code": p.vendor_code,
                "picture": p.picture,
            }
            for p in page_obj.object_list
        ],
        "facets": sorted_facets,
    })