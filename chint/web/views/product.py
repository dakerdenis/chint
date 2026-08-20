from django.shortcuts import get_object_or_404, render

from apps.catalog.models import Product, ProductDocument, Property, PropertyValue
from apps.catalog.services.category_breadcrumbs import build_category_breadcrumbs

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
}

PRIORITY_PROPERTY_IDS = [
    "8a621f8f-c23b-11ef-a976-cfbfac8d01c2",
    "6c30f610-c23b-11ef-a976-cfbfac8d01c2",
    "60335c25-c23b-11ef-a976-cfbfac8d01c2",
    "7e4a6e1c-c23b-11ef-a976-cfbfac8d01c2",
    "783805c3-c23b-11ef-a976-cfbfac8d01c2",
    "783805d1-c23b-11ef-a976-cfbfac8d01c2",
    "72288375-c23b-11ef-a976-cfbfac8d01c2",
    "662bfb1a-c23b-11ef-a976-cfbfac8d01c2",
    "9669cb2d-c23b-11ef-a976-cfbfac8d01c2",
    "905fa034-c23b-11ef-a976-cfbfac8d01c2",
    "905fa032-c23b-11ef-a976-cfbfac8d01c2",
    "7228838b-c23b-11ef-a976-cfbfac8d01c2",
    "9c7e5659-c23b-11ef-a976-cfbfac8d01c2",
    "9669cb4c-c23b-11ef-a976-cfbfac8d01c2",
]

def product_detail(request, product_id):
    product = get_object_or_404(
        Product.objects.using("catalog").filter(category__isnull=False),
        id=product_id
    )

    lang = request.LANGUAGE_CODE

    # ---------- breadcrumbs ----------
    breadcrumbs = []

    if product.category:
        full_breadcrumbs = build_category_breadcrumbs(product.category)
        trimmed = full_breadcrumbs[2:] if len(full_breadcrumbs) > 2 else []

        for cat in trimmed:
            if lang == "en" and getattr(cat, "name_en", None):
                cat.translated_name = cat.name_en
            elif lang == "az" and getattr(cat, "name_az", None):
                cat.translated_name = cat.name_az
            elif lang == "ka" and getattr(cat, "name_ka", None):
                cat.translated_name = cat.name_ka
            else:
                cat.translated_name = cat.name

        breadcrumbs = trimmed

    # ---------- properties ----------

    pv_queryset = (
        PropertyValue.objects
        .using("catalog")
        .select_related("property")
        .filter(product=product)
    )

    properties = []

    for pv in pv_queryset:

        pid = str(pv.property_id)

        if pid in EXCLUDED_PROPERTY_IDS:
            continue

        prop = pv.property

        # --- название свойства ---
        if lang == "en" and getattr(prop, "name_en", None):
            prop_name = prop.name_en
        elif lang == "az" and getattr(prop, "name_az", None):
            prop_name = prop.name_az
        elif lang == "ka" and getattr(prop, "name_ka", None):
            prop_name = prop.name_ka
        else:
            prop_name = prop.name

        # --- значение ---
        if lang == "en" and pv.value_en:
            value = pv.value_en
        elif lang == "az" and pv.value_az:
            value = pv.value_az
        elif lang == "ka" and pv.value_ka:
            value = pv.value_ka
        else:
            value = pv.value

        properties.append({
            "id": pid,
            "name": prop_name,
            "value": value,
            "unit": pv.etim_unit,
        })
    priority_map = {pid: index for index, pid in enumerate(PRIORITY_PROPERTY_IDS)}

    properties.sort(
        key=lambda x: priority_map.get(x["id"], 9999)
    )







    # ---------- documents ----------
    docs_qs = (
        ProductDocument.objects.using("catalog")
        .filter(product=product, file__isnull=False)
        .order_by("sort_order", "id")
    )

    documents = []
    for d in docs_qs:
        if lang == "en" and d.title_en:
            title = d.title_en
        elif lang == "az" and d.title_az:
            title = d.title_az
        elif lang == "ka" and d.title_ka:
            title = d.title_ka
        else:
            title = d.title_ru or d.title_en or d.title_az or d.title_ka or "Document"

        documents.append({
            "title": title,
            "url": d.file.url if d.file else "",
        })

    return render(request, "pages/product-detail.html", {
        "product": product,
        "properties": properties,
        "breadcrumbs": breadcrumbs,
        "documents": documents,
    })
