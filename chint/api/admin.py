from django.contrib import admin
from django.db import models
from django.forms import Textarea

from .models import Product, ProductGroup, CatalogCategory


@admin.register(ProductGroup)
class ProductGroupAdmin(admin.ModelAdmin):
    list_display = ("name_ru", "group_id", "parent_id", "updated_at")
    search_fields = ("name_ru", "name_en", "name_az", "name_ka", "group_id", "parent_id")
    list_filter = ("updated_at",)
    ordering = ("name_ru",)
    readonly_fields = ("updated_at", "source_hash")

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("vendor_code", "name_short_ru", "parent_id", "updated_at")
    search_fields = (
        "vendor_code",
        "name_short_ru", "name_full_ru",
        "name_short_en", "name_full_en",
        "name_short_az", "name_full_az",
        "name_short_ka", "name_full_ka",
        "chint_id", "parent_id"
    )
    list_filter = ("updated_at", "parent_id")
    ordering = ("vendor_code",)
    readonly_fields = ("updated_at", "source_hash")

    # чтобы длинные тексты и JSON нормально редактировались/просматривались
    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": 4, "cols": 80})},
        models.JSONField: {"widget": Textarea(attrs={"rows": 6, "cols": 80})},
    }


@admin.register(CatalogCategory)
class CatalogCategoryAdmin(admin.ModelAdmin):
    list_display = ("name_ru", "slug", "parent", "sort_order", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name_ru", "name_en", "name_az", "name_ka", "slug")
    ordering = ("sort_order", "name_ru")
    autocomplete_fields = ("parent",)
    prepopulated_fields = {"slug": ("name_en",)}
    readonly_fields = ("created_at", "updated_at")

    # ✅ удобный выбор ManyToMany: 2 списка + поиск в обоих
    filter_horizontal = ("product_groups",)
