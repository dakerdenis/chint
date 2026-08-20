from django.urls import path

from web.views.all_goods import all_goods
from web.views.catalog import (
    catalog,
    catalog_category,
    catalog_group,
    catalog_subcategory,
)
from web.views.catalog_products import category_products
from web.views.forms import submit_contact_form
from web.views.news import news_detail
from web.views.pages import (
    about,
    consent_newsletter,
    contacts,
    cookie_policy,
    home,
    library,
    library_tab_api,
    news,
    ng7,
    privacy_policy,
    tech_consult,
    user_agreement,
    where_buy,
)
from web.views.product import product_detail
from web.views.search import search, search_products

app_name = "web"

urlpatterns = [
    path("", home, name="home"),
    path("about/", about, name="about"),
    path("contacts/", contacts, name="contacts"),
    path("catalog/", catalog, name="catalog"),
    path("catalog/<slug:category_slug>/", catalog_category, name="catalog_category"),
    path(
        "catalog/<slug:category_slug>/<slug:sub_slug>/",
        catalog_subcategory,
        name="catalog_subcategory",
    ),
    path(
        "catalog/<slug:category_slug>/<slug:sub_slug>/<slug:group_id>/",
        catalog_group,
        name="catalog_group",
    ),
    path("product/<slug:product_id>/", product_detail, name="product_detail"),
    path("all-goods/", all_goods, name="all_goods"),
    path("news/", news, name="news"),
    path("news/<slug:slug>/", news_detail, name="news_detail"),
    path("where-buy/", where_buy, name="where_buy"),
    path("ng7/", ng7, name="ng7"),
    path("tech-consult/", tech_consult, name="tech_consult"),
    path("library/", library, name="library"),
    path("contact-form/", submit_contact_form, name="contact_form_submit"),
    path(
        "catalog-products/<uuid:category_id>/",
        category_products,
        name="catalog_products",
    ),
    path("politics/user-agreement/", user_agreement, name="user_agreement"),
    path("politics/privacy-policy/", privacy_policy, name="privacy_policy"),
    path("politics/consent-newsletter/", consent_newsletter, name="consent_newsletter"),
    path("politics/cookie/", cookie_policy, name="cookie_policy"),
    path("search/", search, name="search"),
    path("library/api/", library_tab_api, name="library_tab_api"),
    path("search/", search, name="search"),
    path("search-products/", search_products, name="search_products"),
]
