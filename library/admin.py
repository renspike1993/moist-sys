# admin.py
from django.contrib import admin
from .models import Marc21FieldCategory, Marc21Field

# Inline for child fields
class Marc21FieldInline(admin.TabularInline):
    model = Marc21Field
    extra = 0  # No extra empty rows
    fields = ("field_code", "field_name", "label", "is_searchable", "is_hidden")
    readonly_fields = ()
    show_change_link = True


@admin.register(Marc21FieldCategory)
class Marc21FieldCategoryAdmin(admin.ModelAdmin):
    list_display = ("code_range", "description")
    search_fields = ("code_range", "description")
    inlines = [Marc21FieldInline]


@admin.register(Marc21Field)
class Marc21FieldAdmin(admin.ModelAdmin):
    list_display = ("field_code", "label", "category", "is_searchable", "is_hidden")
    list_filter = ("category", "is_searchable", "is_hidden")
    search_fields = ("field_code", "field_name", "label")
