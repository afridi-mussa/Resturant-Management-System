"""
Django admin configuration for the ordering app.

Registering a model here makes it manageable at /admin/. Each ModelAdmin
class customises how that model's list and forms look in the admin site.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import CustomerProfile, Category, MenuItem, Order


# Replace the default User admin so that a logged-in admin can neither see
# nor delete their own account in the Users section.
admin.site.unregister(User)         # remove Django's built-in User admin first


@admin.register(User)               # then register our customised version
class CustomUserAdmin(UserAdmin):
    def get_queryset(self, request):
        # Hide the currently logged-in admin's own row from the user list.
        queryset = super().get_queryset(request)
        return queryset.exclude(pk=request.user.pk)

    def has_delete_permission(self, request, obj=None):
        # Hard block on deleting yourself (defense-in-depth, even via direct URL).
        if obj is not None and obj.pk == request.user.pk:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "address")          # columns in the table
    search_fields = ("user__username", "user__email", "phone", "address")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name", "description")


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_available")
    list_filter = ("is_available", "category")           # right-hand filter sidebar
    search_fields = ("name", "description")
    list_editable = ("price", "is_available")            # edit these straight from the list


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_amount", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__email", "id")
    filter_horizontal = ("items",)                       # nicer widget for the M2M items
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"                        # date drill-down navigation
