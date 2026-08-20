from django.db import models
from django.core.validators import RegexValidator
from django.utils.text import slugify

class ProductGroup(models.Model):
    group_id = models.CharField(max_length=36, unique=True, db_index=True)
    parent_id = models.CharField(max_length=36, blank=True, default="", db_index=True)

    name_ru = models.CharField(max_length=255, blank=True, default="")
    name_en = models.CharField(max_length=255, blank=True, default="")
    name_az = models.CharField(max_length=255, blank=True, default="")
    name_ka = models.CharField(max_length=255, blank=True, default="")

    # NEW: картинка для группы (загружаешь руками)
    image = models.ImageField(upload_to="catalog/product-groups/", blank=True, null=True)

    source_hash = models.CharField(max_length=64, blank=True, default="", db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name_ru or self.name_en or self.name_az or self.name_ka or self.group_id
    
    

class Product(models.Model):
    chint_id = models.CharField(max_length=36, unique=True, db_index=True)
    parent_id = models.CharField(max_length=36, blank=True, default="", db_index=True)

    vendor_code = models.CharField(max_length=64, unique=True, db_index=True)

    name_full_ru = models.TextField(blank=True, default="")
    name_short_ru = models.TextField(blank=True, default="")
    
    name_full_en = models.TextField(blank=True, default="")
    name_short_en = models.TextField(blank=True, default="")
    
    name_full_az = models.TextField(blank=True, default="")
    name_short_az = models.TextField(blank=True, default="")
    
    name_full_ka = models.TextField(blank=True, default="")
    name_short_ka = models.TextField(blank=True, default="")


    picture_url = models.URLField(max_length=500, blank=True, default="")
    images = models.JSONField(default=list, blank=True)

    source_hash = models.CharField(max_length=64, blank=True, default="", db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        title = self.name_short_ru or self.name_full_ru or self.vendor_code
        return f"{self.vendor_code} - {title}"


slug_en_validator = RegexValidator(
    regex=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    message="Slug must be lowercase English (a-z, 0-9, hyphens). Example: low-voltage-equipment"
)

class CatalogCategory(models.Model):
    # дерево
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        db_index=True,
    )
    product_groups = models.ManyToManyField(
        "ProductGroup",
        blank=True,
        related_name="catalog_categories",
    )
    # slug строго EN
    slug = models.SlugField(max_length=160, unique=True, validators=[slug_en_validator])

    # имена
    name_ru = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    name_az = models.CharField(max_length=255)
    name_ka = models.CharField(max_length=255, blank=True, default="")

    # картинка (загружаешь руками)
    image = models.ImageField(upload_to="catalog/categories/", blank=True, null=True)

    # порядок вывода
    sort_order = models.PositiveIntegerField(default=0, db_index=True)

    is_active = models.BooleanField(default=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("sort_order", "name_ru")

    def __str__(self):
        return self.name_ru

    def clean(self):
        # страховка: если кто-то вставит кириллицу в slug
        if self.slug:
            self.slug = slugify(self.slug).lower()

    @property
    def level(self) -> int:
        lvl = 0
        p = self.parent
        while p:
            lvl += 1
            p = p.parent
        return lvl