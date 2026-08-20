import uuid

from django.db import models


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
    )

    # основной (RU)
    name = models.CharField(max_length=255)

    # переводы
    name_en = models.CharField(max_length=255, blank=True)
    name_az = models.CharField(max_length=255, blank=True)
    name_ka = models.CharField(max_length=255, blank=True)

    # картинка категории
    image = models.ImageField(
        upload_to="catalog/categories/",
        blank=True,
        null=True
    )

    class Meta:
        app_label = "catalog"
        ordering = ["name"]
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        managed = True

    def __str__(self):
        return self.name
