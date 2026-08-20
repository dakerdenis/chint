# web/views/pages.py

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from apps.catalog.models import Category, Product
from web.models import (
    HomeFeaturedCategory,
    HomeRecommendedProduct,
    HomeSlider,
    LibraryDocument,
    News,
)


def home(request):
    latest_news = (
        News.objects.filter(is_active=True)
        .order_by("-published_at", "-id")[:3]
    )

    sliders = (
        HomeSlider.objects
        .filter(is_active=True)
        .order_by("sort_order")
    )

    # --- FEATURED CATEGORIES ---
    featured_raw = (
        HomeFeaturedCategory.objects
        .filter(is_active=True)
        .order_by("sort_order")[:8]
    )

    featured_categories = []

    for item in featured_raw:
        try:
            cat = Category.objects.using("catalog").get(id=item.category_id)
            featured_categories.append(cat)
        except Category.DoesNotExist:
            pass

    # --- RECOMMENDED PRODUCTS ---
    recommended_raw = (
        HomeRecommendedProduct.objects
        .filter(is_active=True)
        .order_by("sort_order")[:12]
    )

    recommended_products = []

    for item in recommended_raw:
        try:
            p = Product.objects.using("catalog").get(id=item.product_id)
            recommended_products.append(p)
        except Product.DoesNotExist:
            pass

    return render(request, "pages/home.html", {
        "sliders": sliders,
        "latest_news": latest_news,
        "featured_categories": featured_categories,
        "recommended_products": recommended_products,
    })


def about(request):
    return render(request, "pages/about.html")


def contacts(request):
    return render(request, "pages/contacts.html")


def where_buy(request):
    return render(request, "pages/where-buy.html")


def ng7(request):
    return render(request, "pages/ng7.html")


def tech_consult(request):
    return render(request, "pages/tech-consult.html")



def library(request):
    """Main library page — renders shell with tabs, first tab loaded."""
    active_tab = request.GET.get("tab", "0")
    try:
        active_tab = int(active_tab)
    except ValueError:
        active_tab = 0

    # Load first page for active tab only
    documents = (
        LibraryDocument.objects
        .filter(is_active=True, tab_index=active_tab)
        .order_by("sort_order")
    )
    paginator = Paginator(documents, 10)
    page_obj = paginator.get_page(1)

    return render(request, "pages/library.html", {
        "active_tab": active_tab,
        "page_obj": page_obj,
        "total_tabs": 6,
    })


def library_tab_api(request):
    """AJAX endpoint: GET /library/api/?tab=0&page=1&q=search"""
    tab = request.GET.get("tab", "")
    page_num = request.GET.get("page", "1")
    query = request.GET.get("q", "").strip()

    try:
        page_num = int(page_num)
    except ValueError:
        page_num = 1

    documents = LibraryDocument.objects.filter(is_active=True)

    if query:
        # Search across all tabs
        from django.db.models import Q
        lang = getattr(request, 'LANGUAGE_CODE', 'ru')
        q_filter = Q()
        if lang == 'ru':
            q_filter = Q(title_ru__icontains=query)
        elif lang == 'en':
            q_filter = Q(title_en__icontains=query)
        elif lang == 'az':
            q_filter = Q(title_az__icontains=query)
        elif lang == 'ka':
            q_filter = Q(title_ka__icontains=query)
        # Fallback: search all languages
        q_filter = q_filter | Q(title_ru__icontains=query) | Q(title_en__icontains=query)
        documents = documents.filter(q_filter).distinct()
    else:
        # Filter by tab
        try:
            tab = int(tab)
        except ValueError:
            tab = 0
        documents = documents.filter(tab_index=tab)

    documents = documents.order_by("tab_index", "sort_order")

    paginator = Paginator(documents, 10)
    page_obj = paginator.get_page(page_num)

    html = render_to_string("pages/_library_cards.html", {
        "page_obj": page_obj,
        "request": request,
    }, request=request)

    return JsonResponse({
        "html": html,
        "has_previous": page_obj.has_previous(),
        "has_next": page_obj.has_next(),
        "current_page": page_obj.number,
        "total_pages": paginator.num_pages,
        "total_results": paginator.count,
        "query": query,
    })


def news(request):
    qs = News.objects.filter(is_active=True).order_by("-published_at")
    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get("page") or "1")
    return render(request, "pages/news.html", {"page_obj": page_obj})


def user_agreement(request):
    return render(request, "pages/politics/user-agreement.html")


def privacy_policy(request):
    return render(request, "pages/politics/privacy-policy.html")


def consent_newsletter(request):
    return render(request, "pages/politics/consent-newsletter.html")


def cookie_policy(request):
    return render(request, "pages/politics/cookie.html")
