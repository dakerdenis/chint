from django.http import JsonResponse
from django.shortcuts import render
from ..services.chint_api import get
from ..services.catalog_tree import build_tree

ROOT_ALLOWED_ID = "fe5547de-3d84-11df-96f8-000c6ea69372"


# ---------- JSON ----------
def categories(request):
    return JsonResponse(get("/api/product_groups/"))


# ---------- UI ----------
def categories_ui(request):
    resp = get("/api/product_groups/")
    groups = resp["data"]["product_groups"]

    nodes, _ = build_tree(groups)

    allowed_root = nodes.get(ROOT_ALLOWED_ID)
    categories = [allowed_root] if allowed_root else []

    return render(request, "api_test2/categories_tree.html", {
        "categories": categories,
    })
