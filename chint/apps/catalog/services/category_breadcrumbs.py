from apps.catalog.models import Category


def build_category_breadcrumbs(category: Category):
    """
    Возвращает список категорий от корня до текущей
    """
    path = []
    current = category

    while current:
        path.append(current)
        current = current.parent

    return list(reversed(path))
