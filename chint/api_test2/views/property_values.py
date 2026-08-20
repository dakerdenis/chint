from django.http import JsonResponse

from ..services.chint_api import get


def property_values_json(request):
    page = int(request.GET.get("page", 1))


    resp = get("/api/products/", {
        "limit": 100,
        "page": page,
        "properties": "filled",
    })

    values = []

    for p in resp.get("data", {}).get("products", []):
        for pv in p.get("properties", []):
            values.append({
                "product_id": p["id"],
                "property_id": pv.get("property_id"),
                "value": pv.get("value"),
                "etim_unit": pv.get("etim_unit"),
            })

    return JsonResponse({
        "success": True,
        "results": values,
    })
