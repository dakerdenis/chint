from django import template

from web.models import SiteText

register = template.Library()


@register.filter(name="t")
def t(key: str, request) -> str:
    """
    Использование:
      {{ "nav.catalog"|t:request }}
    """
    lang = getattr(request, "LANGUAGE_CODE", "en")
    lang = (lang or "en").split("-")[0]
    return SiteText.get_value(str(key), lang)
