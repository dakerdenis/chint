from django.db import models

from .category import Category


class Product(models.Model):
    id = models.UUIDField(primary_key=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    vendor_code = models.CharField(max_length=64, db_index=True)

    name = models.TextField()
    full_name = models.TextField()
    short_name = models.TextField()

    name_en = models.TextField(blank=True, null=True)
    name_az = models.TextField(blank=True, null=True)
    name_ka = models.TextField(blank=True, null=True)

    full_name_en = models.TextField(blank=True, null=True)
    full_name_az = models.TextField(blank=True, null=True)
    full_name_ka = models.TextField(blank=True, null=True)

    short_name_en = models.TextField(blank=True, null=True)
    short_name_az = models.TextField(blank=True, null=True)
    short_name_ka = models.TextField(blank=True, null=True)


    etim = models.CharField(max_length=64, blank=True)
    status_article = models.CharField(max_length=64, blank=True)

    picture = models.CharField(max_length=1000, blank=True, null=True)
    certificate = models.FileField(
        upload_to="certificates/",
        blank=True,
        null=True
    )
    raw = models.JSONField()  # 🔥 ПОЛНЫЙ RAW как резерв

    class Meta:
        app_label = "catalog"
        ordering = ["vendor_code"]
        verbose_name = "Product"
        verbose_name_plural = "Products"
        managed = True

    def __str__(self):
        return f"{self.vendor_code} – {self.name}"
