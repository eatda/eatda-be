from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserCreationForm, UserChangeForm
from .models import User


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('social_id', 'social_provider', 'email', 'is_superuser')
    list_filter = ('is_superuser',)
    fieldsets = (
        (None, {'fields': ('social_id', 'social_provider', 'email',)}),
        ("Permissions", {'fields': ('is_superuser',)})
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('social_id', 'social_provider', 'email',),
        }),
    )
    search_fields = ('social_id', 'social_provider')
    ordering = ('social_id', 'social_provider')
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
