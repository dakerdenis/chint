import uuid

from django.db import models


class Property(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)  # RU по умолчанию

    name_en = models.CharField(max_length=255, blank=True, default="")
    name_az = models.CharField(max_length=255, blank=True, default="")
    name_ka = models.CharField(max_length=255, blank=True, default="")

    etim = models.CharField(max_length=64, blank=True)

    class Meta:
        app_label = "catalog"
        verbose_name = "Property"
        verbose_name_plural = "Properties"
        managed = True

    def __str__(self):
        return self.name
