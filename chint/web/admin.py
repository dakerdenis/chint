from django import forms
from django.contrib import admin

from apps.catalog.models import Category, Product

from .models import HomeFeaturedCategory, HomeRecommendedProduct, HomeSlider, LibraryDocument, News, NewsImage, SiteText


@admin.register(SiteText)
class SiteTextAdmin(admin.ModelAdmin):
    list_display = ("key", "updated_at")
    search_fields = ("key", "en", "ru", "az", "ka")
    list_filter = ("updated_at",)


class NewsImageInline(admin.TabularInline):
    model = NewsImage
    extra = 0
    max_num = 5  # ✅ максимум 5 картинок
    fields = ("image", "sort_order")


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("published_at", "title_ru", "slug", "is_active", "updated_at")
    list_filter = ("is_active", "published_at")
    search_fields = ("slug", "title_ru", "title_en", "title_az", "title_ka")
    ordering = ("-published_at",)

    prepopulated_fields = {"slug": ("title_en",)}
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Main", {"fields": ("is_active", "published_at", "slug", "cover")}),
        ("Titles", {"fields": ("title_ru", "title_en", "title_az", "title_ka")}),
        ("Text (WYSIWYG)", {"fields": ("body_ru", "body_en", "body_az", "body_ka")}),
        ("System", {"fields": ("created_at", "updated_at")}),
    )

    inlines = [NewsImageInline]

class HomeFeaturedCategoryForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.using("catalog").all(),
        required=True
    )

    class Meta:
        model = HomeFeaturedCategory
        fields = ("category", "is_active", "sort_order")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # если редактируем существующую запись — подставим текущую категорию
        if self.instance and self.instance.pk and self.instance.category_id:
            try:
                self.fields["category"].initial = Category.objects.using("catalog").get(id=self.instance.category_id)
            except Category.DoesNotExist:
                pass

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.category_id = self.cleaned_data["category"].id
        if commit:
            obj.save()
        return obj


@admin.register(HomeFeaturedCategory)
class HomeFeaturedCategoryAdmin(admin.ModelAdmin):
    form = HomeFeaturedCategoryForm
    list_display = ("get_category", "is_active", "sort_order")
    list_filter = ("is_active",)
    ordering = ("sort_order",)
    fields = ("category", "is_active", "sort_order")

    def get_category(self, obj):
        try:
            cat = Category.objects.using("catalog").get(id=obj.category_id)
            return cat.name_en or cat.name
        except Category.DoesNotExist:
            return "—"
    get_category.short_description = "Category"

    def has_add_permission(self, request):
        if HomeFeaturedCategory.objects.count() >= 8:
            return False
        return super().has_add_permission(request)




class HomeRecommendedProductForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.using("catalog").all(),
        required=True
    )

    class Meta:
        model = HomeRecommendedProduct
        fields = ("product", "is_active", "sort_order")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk and self.instance.product_id:
            try:
                self.fields["product"].initial = Product.objects.using("catalog").get(
                    id=self.instance.product_id
                )
            except Product.DoesNotExist:
                pass

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.product_id = self.cleaned_data["product"].id
        if commit:
            obj.save()
        return obj


@admin.register(HomeRecommendedProduct)
class HomeRecommendedProductAdmin(admin.ModelAdmin):
    list_display = ("get_product", "is_active", "sort_order")
    list_filter = ("is_active",)
    ordering = ("sort_order",)
    fields = ("product", "is_active", "sort_order")
    autocomplete_fields = ("product",)

    def get_product(self, obj):
        try:
            p = Product.objects.using("catalog").get(id=obj.product_id)
            return p.short_name or p.name or p.vendor_code
        except Product.DoesNotExist:
            return "—"

    get_product.short_description = "Product"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "product":
            kwargs["queryset"] = Product.objects.using("catalog").all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(HomeSlider)
class HomeSliderAdmin(admin.ModelAdmin):
    list_display = ("title_en", "is_active", "sort_order")
    list_filter = ("is_active",)
    ordering = ("sort_order",)

    fieldsets = (
        ("Status", {
            "fields": ("is_active", "sort_order")
        }),
        ("Images", {
            "fields": ("background", "right_image")
        }),
        ("Tag", {
            "fields": ("tag_ru", "tag_en", "tag_az", "tag_ka")
        }),
        ("Title", {
            "fields": ("title_ru", "title_en", "title_az", "title_ka")
        }),
        ("Text", {
            "fields": ("text_ru", "text_en", "text_az", "text_ka")
        }),
        ("Button", {
            "fields": (
                "button_ru",
                "button_en",
                "button_az",
                "button_ka",
                "button_url",
            )
        }),
    )
@admin.register(LibraryDocument)
class LibraryDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "title_ru",
        "tab_index",
        "sort_order",
        "is_active",
    )
    list_filter = ("tab_index", "is_active")
    ordering = ("tab_index", "sort_order")
    search_fields = ("title_ru", "title_en")

    fieldsets = (
        ("Tab", {
            "fields": ("tab_index", "sort_order", "is_active")
        }),
        ("Titles", {
            "fields": (
                "title_ru",
                "title_en",
                "title_az",
                "title_ka",
            )
        }),
        ("Files", {
            "fields": (
                "icon",
                "file_ru",
                "file_en",
                "file_az",
                "file_ka",
            )
        }),
    )
