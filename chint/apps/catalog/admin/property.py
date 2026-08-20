from django.contrib import admin

from apps.catalog.models import Property


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    using = "catalog"

    list_display = ("name", "etim")
    readonly_fields = ("id",)

    fields = (
        "id",
        "name",
        "name_en",
        "name_az",
        "name_ka",
        "etim",
    )

    search_fields = (
        "name",
        "name_en",
        "name_az",
        "name_ka",
        "etim",
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
