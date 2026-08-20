from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.http import require_POST

RATE_LIMIT = 10  # в час

@require_POST
def submit_contact_form(request):
    ip = request.META.get("REMOTE_ADDR", "unknown")
    cache_key = f"contact_form:{ip}"

    count = cache.get(cache_key, 0)
    if count >= RATE_LIMIT:
        return JsonResponse({
            "success": False,
            "message": "Too many requests. Try later."
        }, status=429)

    cache.set(cache_key, count + 1, 60 * 60)

    name = request.POST.get("name", "").strip()
    phone = request.POST.get("phone", "").strip()
    email = request.POST.get("email", "").strip()
    message = request.POST.get("message", "").strip()

    if not all([name, phone, email, message]):
        return JsonResponse({
            "success": False,
            "message": "Fill all fields."
        })

    # TODO:
    # - сохранить в БД
    # - отправить email
    # - отправить в CRM

    return JsonResponse({
        "success": True,
        "message": "Thank you! We will contact you."
    })
