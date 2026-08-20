def build_tree(groups):
    # id -> node
    nodes = {}
    for g in groups:
        g = dict(g)
        g["children"] = []
        nodes[g["id"]] = g

    roots = []
    for g in nodes.values():
        pid = g.get("parent_id")
        if pid and pid in nodes:
            nodes[pid]["children"].append(g)
        else:
            roots.append(g)

    return nodes, roots


def collect_descendants(category_id, nodes):
    # все потомки включая себя
    ids = set()

    def dfs(cid):
        if cid in ids:
            return
        ids.add(cid)
        for ch in nodes[cid]["children"]:
            dfs(ch["id"])

    if category_id in nodes:
        dfs(category_id)

    return ids


def breadcrumb(category_id, nodes):
    path = []
    cur = nodes.get(category_id)
    while cur:
        path.append(cur)
        pid = cur.get("parent_id")
        cur = nodes.get(pid)
    return list(reversed(path))
