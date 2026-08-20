from django.core.paginator import Paginator
from django.db.models import Count
from django.http import JsonResponse

from apps.catalog.models import Category, Product, PropertyValue
from apps.catalog.services.category_tree import collect_descendant_ids

PER_PAGE = 20
EXCLUDED_PROPERTY_IDS = {
    "edcb252e-6bc4-11f0-a9c6-fcb7586a0682",
    "edcb2565-6bc4-11f0-a9c6-fcb7586a0682",
    "650fcc33-6e1a-11f0-a9c7-c2b26f0426ef",
    "60335c30-c23b-11ef-a976-cfbfac8d01c2",
    "3eaede16-6e0b-11f0-a9c7-c2b26f0426ef",
    "edcb24f7-6bc4-11f0-a9c6-fcb7586a0682",
    "37f8b3a5-6e0b-11f0-a9c7-c2b26f0426ef",
    "905fa031-c23b-11ef-a976-cfbfac8d01c2",
    "783805ac-c23b-11ef-a976-cfbfac8d01c2",
    "60335c29-c23b-11ef-a976-cfbfac8d01c2",
    "e8ea5435-6bc4-11f0-a9c6-fcb7586a0682",
    "e8ea546c-6bc4-11f0-a9c6-fcb7586a0682",

}
PRIORITY_PROPERTY_IDS = [
    "8a621f8f-c23b-11ef-a976-cfbfac8d01c2",
    "4770e18d-a5ce-11f0-a9e1-d1f4d536cf47",
    "6c30f602-c23b-11ef-a976-cfbfac8d01c2",
    "905fa033-c23b-11ef-a976-cfbfac8d01c2",
    "662bfb1a-c23b-11ef-a976-cfbfac8d01c2",
    "72288375-c23b-11ef-a976-cfbfac8d01c2",
    "905fa055-c23b-11ef-a976-cfbfac8d01c2",
    "6c30f610-c23b-11ef-a976-cfbfac8d01c2",
    "9669cb3d-c23b-11ef-a976-cfbfac8d01c2",
    "7e4a6e1c-c23b-11ef-a976-cfbfac8d01c2",
    "60335c25-c23b-11ef-a976-cfbfac8d01c2",
    "783805c3-c23b-11ef-a976-cfbfac8d01c2",
    "783805d1-c23b-11ef-a976-cfbfac8d01c2",
    "9669cb2d-c23b-11ef-a976-cfbfac8d01c2",
    "905fa034-c23b-11ef-a976-cfbfac8d01c2",
    "905fa032-c23b-11ef-a976-cfbfac8d01c2",
    "7228838b-c23b-11ef-a976-cfbfac8d01c2",
    "9c7e5659-c23b-11ef-a976-cfbfac8d01c2",
    "9669cb4c-c23b-11ef-a976-cfbfac8d01c2",
]

def category_products(request, category_id):
    page = int(request.GET.get("page", 1))

    category = Category.objects.using("catalog").get(id=category_id)
    category_ids = collect_descendant_ids(category)

    products_qs = (
        Product.objects.using("catalog")
        .filter(category_id__in=category_ids)
        .exclude(category__isnull=True)
    )

    filters = {}
    for key, values in request.GET.lists():
        if key.startswith("prop_"):
            prop_id = key.replace("prop_", "")
            filters[prop_id] = values

    for prop_id, values in filters.items():
        products_qs = products_qs.filter(
            properties__property_id=prop_id,
            properties__value__in=values
        )

    products_qs = products_qs.distinct().order_by("vendor_code")

    paginator = Paginator(products_qs, PER_PAGE)
    page_obj = paginator.get_page(page)

    lang = request.LANGUAGE_CODE

    facets_qs = (
        PropertyValue.objects.using("catalog")
        .select_related("property")
        .filter(product__category_id__in=category_ids)
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

        facets.setdefault(pid, {
            "name": prop_name,
            "values": []
        })

        # выбираем перевод value
        if lang == "en" and f["value_en"]:
            value_label = f["value_en"]
        elif lang == "az" and f["value_az"]:
            value_label = f["value_az"]
        elif lang == "ka" and f["value_ka"]:
            value_label = f["value_ka"]
        else:
            value_label = f["value"]

        facets[pid]["values"].append({
            "value": f["value"],          # оригинал для фильтрации
            "label": value_label,         # перевод для отображения
            "count": f["count"]
        })

    # ---------- MERGE DUPLICATE VALUES ----------
    for pid in facets:
        merged = {}
        for entry in facets[pid]["values"]:
            v = entry["value"]
            if v in merged:
                merged[v]["count"] += entry["count"]
            else:
                merged[v] = {
                    "value": entry["value"],
                    "label": entry["label"],
                    "count": entry["count"],
                }
        facets[pid]["values"] = list(merged.values())



    # ---------- SORT FACETS ----------
    priority_map = {pid: index for index, pid in enumerate(PRIORITY_PROPERTY_IDS)}

    sorted_facets = dict(
        sorted(
            facets.items(),
            key=lambda x: priority_map.get(x[0], 9999)
        )
    )

    return JsonResponse({
        "count": paginator.count,
        "page": page_obj.number,
        "num_pages": paginator.num_pages,
        "results": [
            {
                "id": str(p.id),

                "name": (
                    p.short_name_en if lang == "en" and p.short_name_en else
                    p.short_name_az if lang == "az" and p.short_name_az else
                    p.short_name_ka if lang == "ka" and p.short_name_ka else
                    p.short_name or
                    p.name_en if lang == "en" and p.name_en else
                    p.name_az if lang == "az" and p.name_az else
                    p.name_ka if lang == "ka" and p.name_ka else
                    p.name
                ),

                "vendor_code": p.vendor_code,
                "picture": p.picture,
            }
            for p in page_obj.object_list
        ],

        "facets": sorted_facets,
    })
