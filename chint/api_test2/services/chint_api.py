import requests
from django.conf import settings

HEADERS = {
    "X-API-KEY": settings.CHINT_API_KEY,
}

def get(path, params=None):
    url = f"{settings.CHINT_API_BASE_URL}{path}"
    r = requests.get(
        url,
        headers=HEADERS,
        params=params or {},
        timeout=settings.CHINT_API_TIMEOUT,
        verify=settings.CHINT_API_CA_BUNDLE,
    )
    return r.json()
