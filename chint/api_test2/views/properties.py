from django.http import JsonResponse

from ..services.chint_api import get


def properties_json(request):
    """
    Прокси к /api/product_properties/
    """
    return JsonResponse(get("/api/product_properties/", request.GET))
