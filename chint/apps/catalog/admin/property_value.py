from django.contrib import admin

from apps.catalog.models import PropertyValue


@admin.register(PropertyValue)
class PropertyValueAdmin(admin.ModelAdmin):
    using = "catalog"

    list_display = ("product", "property", "value")
    autocomplete_fields = ("product", "property")
    readonly_fields = ()

    fields = (
        "product",
        "property",
        "value",
        "value_en",
        "value_az",
        "value_ka",
        "etim_feature",
        "etim_value",
        "etim_unit",
    )

    search_fields = (
        "value",
        "value_en",
        "value_az",
        "value_ka",
        "product__vendor_code",
        "product__name",
        "product__name_en",
        "product__name_az",
        "product__name_ka",
        "product__short_name",
        "product__short_name_en",
        "product__short_name_az",
        "product__short_name_ka",
    )


    def get_queryset(self, request):
        return super().get_queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs["using"] = self.using
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        obj.delete(using=self.using)

    def delete_queryset(self, request, queryset):
        queryset.using(self.using).delete()
