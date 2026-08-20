from django.shortcuts import get_object_or_404, render

from web.models import News


def news_detail(request, slug):
    obj = get_object_or_404(News, slug=slug, is_active=True)
    gallery = obj.images.all()
    return render(request, "pages/news-detail.html", {"news": obj, "gallery": gallery})
