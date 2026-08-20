from django.shortcuts import render, get_object_or_404
from web.models import News


def news_detail(request, slug):
    obj = get_object_or_404(News, slug=slug, is_active=True)
    gallery = obj.images.all()
    return render(request, "pages/news-detail.html", {"news": obj, "gallery": gallery})
