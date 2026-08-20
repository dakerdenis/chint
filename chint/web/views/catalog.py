from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch
from django.core.paginator import Paginator



from api.models import Product, ProductGroup, CatalogCategory
from apps.catalog.services.category_tree import collect_descendant_ids

from apps.catalog.models import Category, Product
from apps.catalog.services.category_breadcrumbs import build_category_breadcrumbs

from django.shortcuts import render, get_object_or_404
ROOT_CATEGORY_TO_HIDE = "fe5547de-3d84-11df-96f8-000c6ea69372"
LOW_VOLTAGE_ID = "4b505b87-6716-11ec-80e8-0025902f52d3"
PER_PAGE = 20

def get_category_name(category, lang):
    if lang == "en" and getattr(category, "name_en", None):
        return category.name_en
    if lang == "az" and getattr(category, "name_az", None):
        return category.name_az
    if lang == "ka" and getattr(category, "name_ka", None):
        return category.name_ka
    return category.name


def _paginate_products(request, qs):
    paginator = Paginator(qs, PER_PAGE)
    return paginator.get_page(request.GET.get("page") or 1)


def catalog(request):
    root = get_object_or_404(
        Category.objects.using("catalog"),
        id=LOW_VOLTAGE_ID
    )

    level1 = (
        Category.objects.using("catalog")
        .filter(parent=root)
        .order_by("name")
        .prefetch_related("children")
    )

    return render(request, "pages/catalog.html", {
        "root": root,
        "root_name": get_category_name(root, request.LANGUAGE_CODE),
        "level1": level1,
    })
def catalog_category(request, category_slug):
    category = get_object_or_404(
        Category.objects.using("catalog"),
        id=category_slug
    )

    subcategories = (
        Category.objects.using("catalog")
        .filter(parent=category)
        .order_by("name")
    )

    # ✅ ВСЕ категории ниже текущей
    category_ids = collect_descendant_ids(category)

    qs = (
        Product.objects.using("catalog")
        .filter(category_id__in=category_ids)
        .exclude(category__isnull=True)
        .order_by("vendor_code")
    )

    page_obj = _paginate_products(request, qs)
    


    breadcrumbs = build_category_breadcrumbs(category)

    # 🔥 Убираем "Готовая продукция"
    breadcrumbs = [
        b for b in breadcrumbs
        if str(b.id) != ROOT_CATEGORY_TO_HIDE
    ]

    lang = request.LANGUAGE_CODE
    for cat in breadcrumbs:
        cat.translated_name = get_category_name(cat, lang)



    return render(request, "pages/catalog-category.html", {
        "category": category,
        "category_name": get_category_name(category, lang),
        "subcategories": subcategories,
        "page_obj": page_obj,
        "breadcrumbs": breadcrumbs,
    })






def catalog_subcategory(request, category_slug, sub_slug):
    parent = get_object_or_404(
        Category.objects.using("catalog"),
        id=category_slug
    )

    current = get_object_or_404(
        Category.objects.using("catalog"),
        id=sub_slug,
        parent=parent
    )

    children = (
        Category.objects.using("catalog")
        .filter(parent=current)
        .order_by("name")
    )

    category_ids = collect_descendant_ids(current)

    qs = (
        Product.objects.using("catalog")
        .filter(category_id__in=category_ids)
        .order_by("vendor_code")
    )

    page_obj = _paginate_products(request, qs)


    breadcrumbs = build_category_breadcrumbs(current)
    
    # 🔥 Убираем "Готовая продукция"
    breadcrumbs = [
        b for b in breadcrumbs
        if str(b.id) != ROOT_CATEGORY_TO_HIDE
    ]
    
    lang = request.LANGUAGE_CODE
    for cat in breadcrumbs:
        cat.translated_name = get_category_name(cat, lang)
    


    return render(request, "pages/catalog-category.html", {
        "category": current,
        "category_name": get_category_name(current, lang),
        "parent": parent,
        "subcategories": children,
        "page_obj": page_obj,
        "breadcrumbs": breadcrumbs,
    })





def catalog_group(request, category_slug, sub_slug, group_id):
    # 3 уровень
    category = get_object_or_404(CatalogCategory, slug=category_slug, is_active=True)
    subcategory = get_object_or_404(CatalogCategory, slug=sub_slug, is_active=True, parent=category)
    pg = get_object_or_404(ProductGroup, group_id=group_id)

    qs = Product.objects.filter(parent_id=group_id).order_by("vendor_code")
    page_obj = _paginate_products(request, qs)

    return render(request, "pages/catalog-category.html", {
        "root": category.parent if category.parent_id else None,
        "category": category,
        "category_name": get_category_name(category, request.LANGUAGE_CODE),
        "subcategory": subcategory,
        "product_group": pg,
        "items": [],
        "page_obj": page_obj,
    })

