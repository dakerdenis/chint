from django.http import JsonResponse
from django.shortcuts import render

from ..services.chint_api import get


# ---------- JSON ----------
def products_json(request):
    return JsonResponse(get("/api/products/", request.GET))


# ---------- UI ----------
def products_ui(request):
    page = int(request.GET.get("page", 1))

    data = get("/api/products/", {
        "limit": 25,
        "page": page,
    })

    return render(request, "api_test2/products_list.html", {
        "products": data["data"]["products"],
        "page": data["data"]["current_page"],
        "pages": data["data"]["pages"],
    })


def product_ui(request, vendor_code):
    product_resp = get("/api/products/", {
        "vendor_code": vendor_code,
        "properties": "filled",
    })

    product = product_resp["data"]["products"][0]

    props_resp = get("/api/product_properties/")
    prop_dict = {p["id"]: p["name"] for p in props_resp["data"]["properties"]}

    enriched_properties = [
        {
            "name": prop_dict.get(p["property_id"], p["property_id"]),
            "value": p["value"],
            "unit": p.get("etim_unit", ""),
        }
        for p in product.get("properties", [])
    ]

    return render(request, "api_test2/product_detail.html", {
        "product": product,
        "properties": enriched_properties,
    })
