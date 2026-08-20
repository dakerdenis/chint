from django.urls import path
from .views import (
    index,
    products_json, products_ui, product_ui,
    categories, categories_ui,
    category_page,
    properties_json,
    property_values_json,
)

urlpatterns = [
    path("", index),

    path("products/", products_json),
    path("products/ui/", products_ui),
    path("products/<str:vendor_code>/", product_ui),

    path("categories/", categories),
    path("categories/ui/", categories_ui),

    path("properties/", properties_json),
    path("property-values/", property_values_json),

    path("catalog/<str:category_id>/", category_page),
]
