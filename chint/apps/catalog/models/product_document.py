from django.db import models
from .product import Product


class ProductDocument(models.Model):
    id = models.BigAutoField(primary_key=True)

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="documents",
    )

    file = models.FileField(upload_to="product_documents/", blank=True, null=True)

    title_ru = models.CharField(max_length=255, blank=True, default="")
    title_en = models.CharField(max_length=255, blank=True, default="")
    title_az = models.CharField(max_length=255, blank=True, default="")
    title_ka = models.CharField(max_length=255, blank=True, default="")

    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        app_label = "catalog"
        ordering = ["sort_order", "id"]
        verbose_name = "Product document"
        verbose_name_plural = "Product documents"
        managed = True

    def __str__(self):
        base = self.title_ru or self.title_en or self.title_az or self.title_ka or "Document"
        return f"{base}"