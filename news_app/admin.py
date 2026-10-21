from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Publisher, Article, Newsletter


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'is_staff', 'is_superuser']
    # Extend the base UserAdmin.fieldsets in a type-safe way
    # Use getattr to ensure we get an iterable even if UserAdmin.fieldsets is None
    fieldsets = list(getattr(UserAdmin, 'fieldsets', [])) + [
        (
            'News App Role & Subscriptions',
            {
                'fields': (
                    'role',
                    'subscribed_publishers',
                    'subscribed_journalists',
                ),
            },
        ),
    ]

    filter_horizontal = (
        'subscribed_publishers',
        'subscribed_journalists',
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Publisher)
admin.site.register(Article)
admin.site.register(Newsletter)
