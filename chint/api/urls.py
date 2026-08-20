from django.urls import path
from . import views
from . import views_local

app_name = "api"

urlpatterns = [
    path("catalog/products/", views.products, name="catalog_products_proxy"),      # прокси к CHINT
    path("catalog/local-products/", views_local.catalog_products, name="catalog_products_local"),  # из БД
]
