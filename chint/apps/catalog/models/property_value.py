from django.db import models

from .product import Product
from .property import Property


class PropertyValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="properties")
    property = models.ForeignKey(
        Property,
        on_delete=models.DO_NOTHING,
        db_constraint=False,
        related_name="values",
    )


    value = models.CharField(max_length=255, blank=True)

    value_en = models.CharField(max_length=255, blank=True, null=True)
    value_az = models.CharField(max_length=255, blank=True, null=True)
    value_ka = models.CharField(max_length=255, blank=True, null=True)

    etim_feature = models.CharField(max_length=64, blank=True)
    etim_value = models.CharField(max_length=64, blank=True)
    etim_unit = models.CharField(max_length=64, blank=True)


    class Meta:
        app_label = "catalog"
        verbose_name = "Property value"
        verbose_name_plural = "Property values"
        unique_together = ("product", "property")
        managed = True
