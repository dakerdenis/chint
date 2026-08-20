from ckeditor_uploader.fields import RichTextUploadingField
from django.core.cache import cache
from django.core.validators import RegexValidator
from django.db import models
from django.utils.text import slugify

from apps.catalog.models import Category, Product


# --------------------
# SITE TEXT
# --------------------
class SiteText(models.Model):
    key = models.CharField(max_length=120, unique=True, db_index=True)
    en = models.TextField(blank=True, default="")
    ru = models.TextField(blank=True, default="")
    az = models.TextField(blank=True, default="")
    ka = models.TextField(blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("key",)

    def __str__(self):
        return self.key

    @staticmethod
    def get_value(key: str, lang: str) -> str:
        lang = (lang or "en").split("-")[0]
        cache_key = f"site_text:{lang}:{key}"

        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        obj = SiteText.objects.filter(key=key).first()
        if not obj:
            cache.set(cache_key, key, 60)
            return key

        value = getattr(obj, lang, "") or obj.en or key
        cache.set(cache_key, value, 600)
        return value



slug_en_validator = RegexValidator(
    regex=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    message="Slug must be lowercase English.",
)


class News(models.Model):
    slug = models.SlugField(max_length=180, unique=True, validators=[slug_en_validator])

    title_ru = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)
    title_az = models.CharField(max_length=255, blank=True, default="")
    title_ka = models.CharField(max_length=255, blank=True, default="")

    body_ru = RichTextUploadingField(blank=True, default="")
    body_en = RichTextUploadingField(blank=True, default="")
    body_az = RichTextUploadingField(blank=True, default="")
    body_ka = RichTextUploadingField(blank=True, default="")

    cover = models.ImageField(upload_to="news/covers/")
    published_at = models.DateTimeField(db_index=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-published_at", "-id")

    def __str__(self):
        return self.title_ru or self.title_en or self.slug


class NewsImage(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="news/gallery/")
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("sort_order", "id")


class HomeFeaturedCategory(models.Model):
    category_id = models.UUIDField()
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("sort_order", "id")

    def __str__(self):
        return str(self.category_id)


class HomeRecommendedProduct(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        db_constraint=False,
    )
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("sort_order", "id")

    def __str__(self):
        return str(self.product_id)



class HomeSlider(models.Model):
    is_active = models.BooleanField(default=True, db_index=True)
    sort_order = models.PositiveIntegerField(default=0, db_index=True)

    # фон
    background = models.ImageField(
        upload_to="home/slider/backgrounds/"
    )
    # 👉 ПРАВАЯ КАРТИНКА (ВОТ ЕЁ НЕ ХВАТАЛО)
    right_image = models.ImageField(
        upload_to="home/slider/images/",
        blank=True,
        null=True,
    )
    # TAG
    tag_ru = models.CharField(max_length=255, blank=True, default="")
    tag_en = models.CharField(max_length=255, blank=True, default="")
    tag_az = models.CharField(max_length=255, blank=True, default="")
    tag_ka = models.CharField(max_length=255, blank=True, default="")

    # TITLE
    title_ru = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)
    title_az = models.CharField(max_length=255, blank=True, default="")
    title_ka = models.CharField(max_length=255, blank=True, default="")

    # TEXT
    text_ru = models.TextField(blank=True, default="")
    text_en = models.TextField(blank=True, default="")
    text_az = models.TextField(blank=True, default="")
    text_ka = models.TextField(blank=True, default="")

    # BUTTON
    button_ru = models.CharField(max_length=255, blank=True, default="")
    button_en = models.CharField(max_length=255, blank=True, default="")
    button_az = models.CharField(max_length=255, blank=True, default="")
    button_ka = models.CharField(max_length=255, blank=True, default="")
    button_url = models.URLField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("sort_order", "id")
        verbose_name = "Home slider"
        verbose_name_plural = "Home sliders"

    def __str__(self):
        return self.title_en or self.title_ru

# --------------------
# LIBRARY
# --------------------
class LibraryDocument(models.Model):
    TAB_CHOICES = (
        (0, "Мастер-каталог (New)"),
        (1, "Техническая документация"),
        (2, "Рекламные материалы"),
        (3, "Сертификаты"),
        (4, "Для проектировщиков"),
        (5, "Средневольтное оборудование"),
    )

    tab_index = models.PositiveSmallIntegerField(choices=TAB_CHOICES)

    title_ru = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)
    title_az = models.CharField(max_length=255, blank=True, default="")
    title_ka = models.CharField(max_length=255, blank=True, default="")

    # ✅ НОВОЕ ПОЛЕ
    icon = models.ImageField(
        upload_to="library/icons/",
        blank=True,
        null=True,
    )

    file_ru = models.FileField(upload_to="library/ru/")
    file_en = models.FileField(upload_to="library/en/",blank=True, null=True)
    file_az = models.FileField(upload_to="library/az/", blank=True, null=True)
    file_ka = models.FileField(upload_to="library/ka/", blank=True, null=True)

    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("tab_index", "sort_order", "id")

    def __str__(self):
        return self.title_ru or self.title_en
