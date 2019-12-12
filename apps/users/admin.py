from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.users.models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    pass


# admin.site.register(UserProfile, UserProfileAdmin)  老式的admin_user表
# admin.site.register(UserProfile, UserAdmin)  # 新式的
