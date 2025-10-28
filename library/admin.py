# admin.py
from django.contrib import admin
from .models import (
    Department,
    Program,
    Marc21FieldCategory,
    Marc21Field,
    Book,
    BookDetail,
    Transaction,
    TransactionItem,
)

# ===========================
# 📘 MARC21 FIELD STRUCTURE
# ===========================

class Marc21FieldInline(admin.TabularInline):
    model = Marc21Field
    extra = 0
    fields = ("field_code", "field_name", "label", "is_searchable", "is_hidden")
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

# ===========================
# 📚 BOOK & DETAILS
# ===========================

class BookDetailInline(admin.TabularInline):
    model = BookDetail
    extra = 1
    fields = ("marc21_field", "value")
    show_change_link = True


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("id", "program", "created_at", "updated_at")
    list_filter = ("program",)
    search_fields = ("id",)
    inlines = [BookDetailInline]


@admin.register(BookDetail)
class BookDetailAdmin(admin.ModelAdmin):
    list_display = ("book", "marc21_field", "value")
    list_filter = ("marc21_field",)
    search_fields = ("value",)

# ===========================
# 🧑‍🎓 PROGRAMS & DEPARTMENTS
# ===========================

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("id", "abbrv", "name", "department")
    list_filter = ("department",)
    search_fields = ("abbrv", "name")

# ===========================
# 🔄 TRANSACTIONS
# ===========================

class TransactionItemInline(admin.TabularInline):
    model = TransactionItem
    extra = 0
    fields = ("book", "status", "quantity", "reserved_at")
    readonly_fields = ("reserved_at",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("transaction_id", "user_id", "status", "reservation_date", "checkout_date", "due_date")
    list_filter = ("status",)
    search_fields = ("transaction_id", "user_id", "user_name")
    inlines = [TransactionItemInline]


@admin.register(TransactionItem)
class TransactionItemAdmin(admin.ModelAdmin):
    list_display = ("transaction", "book", "status", "reserved_at")
    list_filter = ("status",)
    search_fields = ("transaction__transaction_id", "book__id")

