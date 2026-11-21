from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


from .models import CustomUser, Role, CustomPermission
from .forms import UserCreationForm, UserChangeForm


@admin.register(CustomPermission)
class CustomPermissionAdmin(admin.ModelAdmin):
    list_display = ("name", "description")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "description")


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ["first_name", "last_name", "email", "date_of_birth", "is_admin", "is_superuser", "is_deleted"]
    list_filter = ["is_admin"]
    fieldsets = [
        (None, {"fields": ["email", "first_name", "last_name", "password", "is_deleted", "is_active"]}),
        ("Permissions", {"fields": ["is_admin", "is_superuser", "roles"]}),
    ]

    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "first_name", "last_name", "date_of_birth", "password1", "password2", "roles"],
            },
        ),
    ]
    search_fields = ["email"]
    ordering = ["email"]
    filter_horizontal = []


admin.site.register(CustomUser, UserAdmin)
admin.site.unregister(Group)
