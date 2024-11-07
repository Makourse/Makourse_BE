from django.contrib import admin
from .models import *

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
admin.site.register(User, UserAdmin)


admin.site.register(UserGroup)