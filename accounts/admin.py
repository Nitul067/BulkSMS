from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile


admin.site.site_header = "BulkSMS Administration"
admin.site.site_title = "Admin"
admin.site.index_title = "BulkSMS"

User.get_short_name = lambda user_instance: user_instance.first_name


class CustomUserAdmin(UserAdmin):
    list_display = ("email", "first_name", "last_name", "username", "is_active")
    ordering = ("-date_joined",)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.unregister(Group)

admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile)
