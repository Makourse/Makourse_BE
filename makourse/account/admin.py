from django.contrib import admin
from .models import *

class CutomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'social_provider', 'profile_image', 'is_logged_in')
admin.site.register(CustomUser, CutomUserAdmin)

# class UserAdmin(admin.ModelAdmin):
#     list_display = ('pk', 'email', 'name', 'social_provider', 'profile_image', 'is_logged_in')
# admin.site.register(User, UserAdmin)


admin.site.register(UserGroup)
admin.site.register(GroupMembership)
