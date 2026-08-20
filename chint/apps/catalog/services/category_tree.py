from apps.catalog.models import Category


def collect_descendant_ids(root: Category, using="catalog"):
    """
    Возвращает список ID категории + всех её потомков
    """
    ids = []

    def dfs(node):
        ids.append(node.id)
        children = Category.objects.using(using).filter(parent=node)
        for ch in children:
            dfs(ch)

    dfs(root)
    return ids
