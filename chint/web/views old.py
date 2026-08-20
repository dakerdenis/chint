from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch

from django.core.paginator import Paginator
from django.db.models import Q


from api.models import Product, ProductGroup, CatalogCategory

def home(request):
    return render(request, 'pages/home.html')

def about(request):
    return render(request, 'pages/about.html')

def contacts(request):
    return render(request, 'pages/contacts.html')


def news(request):
    return render(request, 'pages/news.html')



def catalog(request):
    # Загружаем дерево: root -> children -> grandchildren
    roots = (
        CatalogCategory.objects
        .filter(is_active=True, parent__isnull=True)
        .order_by("sort_order", "name_ru")
        .prefetch_related(
            Prefetch(
                "children",
                queryset=CatalogCategory.objects.filter(is_active=True)
                .order_by("sort_order", "name_ru")
                .prefetch_related(
                    Prefetch(
                        "children",
                        queryset=CatalogCategory.objects.filter(is_active=True)
                        .order_by("sort_order", "name_ru")
                    )
                )
            )
        )
    )

    return render(request, "pages/catalog.html", {
        "roots": roots,
    })


    
    
def all_goods(request):
    q = (request.GET.get("q") or "").strip()
    page_number = request.GET.get("page") or "1"

    group = (request.GET.get("group") or "").strip()

    qs = Product.objects.all()
    groups = ProductGroup.objects.order_by("name_ru").only("group_id", "name_ru")

    if group:
        qs = qs.filter(parent_id=group)

    if q:
        qs = qs.filter(
            Q(vendor_code__icontains=q) |
            Q(name_short_ru__icontains=q) |
            Q(name_full_ru__icontains=q)
        )

    qs = qs.order_by("vendor_code")

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(page_number)

    return render(request, "pages/all-goods.html", {
        "page_obj": page_obj,
        "q": q,
        "group": group,
        "groups": groups,
    })
    
def catalog_category(request, category_slug):
    category = get_object_or_404(CatalogCategory, slug=category_slug, is_active=True)

    root = category.parent if category.parent_id else None

    child_cats = list(
        CatalogCategory.objects
        .filter(parent=category, is_active=True)
        .order_by("sort_order", "name_ru")
    )

    # items = только категории 2-го уровня
    items = []
    for c in child_cats:
        items.append({
            "kind": "category",
            "obj": c,
            "href": f"/{request.LANGUAGE_CODE}/catalog/{category.slug}/{c.slug}/",
            "image_url": c.image.url if c.image else "",
        })

    return render(request, "pages/catalog-category.html", {
        "root": root,
        "category": category,
        "subcategory": None,
        "product_group": None,
        "items": items,
    })

def catalog_subcategory(request, category_slug, sub_slug):
    category = get_object_or_404(CatalogCategory, slug=category_slug, is_active=True)
    root = category.parent if category.parent_id else None

    subcategory = get_object_or_404(
        CatalogCategory,
        slug=sub_slug,
        is_active=True,
        parent=category
    )

    pgs = list(subcategory.product_groups.all().order_by("name_ru"))

    items = []
    for g in pgs:
        items.append({
            "kind": "group",
            "obj": g,
            "href": f"/{request.LANGUAGE_CODE}/catalog/{category.slug}/{subcategory.slug}/{g.group_id}/",
            "image_url": g.image.url if g.image else "",
        })

    return render(request, "pages/catalog-category.html", {
        "root": root,
        "category": category,
        "subcategory": subcategory,
        "product_group": None,
        "items": items,
    })



def catalog_group(request, category_slug, sub_slug, group_id):
    category = get_object_or_404(CatalogCategory, slug=category_slug, is_active=True)
    subcategory = get_object_or_404(CatalogCategory, slug=sub_slug, is_active=True, parent=category)
    pg = get_object_or_404(ProductGroup, group_id=group_id)

    page_number = request.GET.get("page") or "1"

    qs = Product.objects.filter(parent_id=group_id).order_by("vendor_code")
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(page_number)

    return render(request, "pages/catalog-category.html", {
        "root": category.parent if category.parent_id else None,
        "category": category,
        "subcategory": subcategory,
        "product_group": pg,
        "items": [],          # на этом уровне items не нужны
        "page_obj": page_obj, # товары
    })



