from django.test import Client
from django.db import transaction
from apps.catalog.models import PropertyValue


def import_property_values():
    client = Client()

    page = 1
    limit = 500

    while True:
        response = client.get(
            "/api-test2/property-values/",
            {
                "limit": limit,
                "page": page,
            }
        )

        data = response.json()
        rows = data.get("results", [])

        if not rows:
            break

        with transaction.atomic(using="catalog"):
            for r in rows:
                PropertyValue.objects.using("catalog").update_or_create(
                    product_id=r["product_id"],
                    property_id=r["property_id"],
                    defaults={
                        "value": r.get("value", ""),
                        "etim_unit": r.get("etim_unit", ""),
                    }
                )

        page += 1
