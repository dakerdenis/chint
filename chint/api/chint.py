import time

import requests
from django.conf import settings


def chint_get(path: str, params: dict | None = None) -> dict:
    url = settings.CHINT_API_BASE_URL.rstrip("/") + path
    headers = {"X-API-KEY": settings.CHINT_API_KEY, "Accept": "application/json"}

    timeout = getattr(settings, "CHINT_API_TIMEOUT", 45)
    verify = getattr(settings, "CHINT_API_CA_BUNDLE", True)  # или True/False, как у тебя настроено

    attempts = 5
    backoff = 1.5

    last_exc = None
    for i in range(attempts):
        try:
            r = requests.get(url, headers=headers, params=params or {}, timeout=timeout, verify=verify)
            r.raise_for_status()
            return r.json()
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout,
                requests.exceptions.ConnectionError) as e:
            last_exc = e
            # экспоненциальная пауза: 1.5s, 2.25s, 3.4s...
            time.sleep(backoff ** (i + 1))
            continue

    raise last_exc
