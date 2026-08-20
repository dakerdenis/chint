from django.contrib import admin
from django import forms
from django.core.files.storage import default_storage
from django.utils import timezone

import os
import uuid

from apps.catalog.models import Product, ProductDocument


class ProductDocumentInline(admin.TabularInline):
    model = ProductDocument
    extra = 1
    min_num = 0
    fields = (
        "sort_order",
        "file",
        "title_ru",
        "title_en",
        "title_az",
        "title_ka",
    )
    ordering = ("sort_order", "id")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.using("catalog")


class ProductAdminForm(forms.ModelForm):
    upload_image = forms.ImageField(
        required=False,
        label="Upload image (optional)",
        help_text="Used only if Picture URL is empty. Saved to /media/product/images/."
    )

    # ✅ raw делаем необязательным в админке
    raw = forms.JSONField(required=False)

    class Meta:
        model = Product
        fields = "__all__"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    using = "catalog"

    form = ProductAdminForm

    list_display = ("vendor_code", "name", "category")
    readonly_fields = ("id",)
    inlines = (ProductDocumentInline,)

    fields = (
        "id",
        "category",
        "vendor_code",

        "name",
        "name_en",
        "name_az",
        "name_ka",

        "short_name",
        "short_name_en",
        "short_name_az",
        "short_name_ka",

        "full_name",
        "full_name_en",
        "full_name_az",
        "full_name_ka",

        "etim",
        "status_article",

        "picture",        # ✅ URL (приоритет)
        "upload_image",   # ✅ загрузка файла (fallback)
        "certificate",
        "raw",
    )

    search_fields = (
        "vendor_code",
        "name",
        "name_en",
        "name_az",
        "name_ka",
        "short_name",
        "short_name_en",
        "short_name_az",
        "short_name_ka",
        "full_name",
        "full_name_en",
        "full_name_az",
        "full_name_ka",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs["using"] = self.using
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    


    def save_model(self, request, obj, form, change):
        uploaded = form.cleaned_data.get("upload_image")
    
        # ✅ FIX: если добавляем новый продукт и id пустой — генерим UUID (как в твоей базе)
        if not obj.id:
            obj.id = uuid.uuid1()
    
        # ✅ если raw не заполнено — ставим пустой объект
        if not obj.raw:
            obj.raw = {}
    
        if (not obj.picture) and uploaded:
            ext = os.path.splitext(uploaded.name)[1].lower() or ".jpg"
            fname = f"{uuid.uuid4().hex}{ext}"
            path = f"product/images/{timezone.now().strftime('%Y/%m')}/{fname}"
    
            saved_path = default_storage.save(path, uploaded)
            obj.picture = default_storage.url(saved_path)
    
        obj.save(using=self.using)
            
        
        
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for obj in formset.deleted_objects:
            obj.delete(using=self.using)

        for obj in instances:
            obj.save(using=self.using)

        formset.save_m2m()

    def delete_model(self, request, obj):
        obj.delete(using=self.using)

    def delete_queryset(self, request, queryset):
        queryset.using(self.using).delete()