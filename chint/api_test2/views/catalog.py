from django.shortcuts import render

from ..services.catalog_tree import breadcrumb, build_tree, collect_descendants
from ..services.chint_api import get

ROOT_ALLOWED_ID = "fe5547de-3d84-11df-96f8-000c6ea69372"


def category_page(request, category_id):
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 25))
    if limit not in (25, 50, 100):
        limit = 25

    resp = get("/api/product_groups/")
    groups = resp["data"]["product_groups"]
    nodes, _ = build_tree(groups)

    # 🔒 защита от "Вывод из ассортимента"
    allowed_ids = collect_descendants(ROOT_ALLOWED_ID, nodes)
    if category_id not in allowed_ids:
        return render(request, "api_test2/category_page.html", {
            "category": None,
            "children": [],
            "products": [],
            "page": 1,
            "pages": 1,
            "breadcrumb": [],
        })

    current = nodes.get(category_id)
    children = current["children"]

    descendant_ids = collect_descendants(category_id, nodes)
    leaf_ids = [cid for cid in descendant_ids if not nodes[cid]["children"]]

    all_products = []
    for leaf_id in leaf_ids:
        resp = get("/api/products/", {
            "parent_id": leaf_id,
            "limit": 0,
        })
        if resp.get("success"):
            all_products.extend(resp["data"].get("products", []))

    total = len(all_products)
    pages = max(1, (total + limit - 1) // limit)

    start = (page - 1) * limit
    end = start + limit

    return render(request, "api_test2/category_page.html", {
        "category": current,
        "children": children,
        "products": all_products[start:end],
        "page": page,
        "pages": pages,
        "limit": limit,
        "breadcrumb": breadcrumb(category_id, nodes),
    })
