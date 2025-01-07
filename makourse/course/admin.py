from django.contrib import admin
from .models import *

class MyPlaceAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'place_name')
admin.site.register(MyPlace, MyPlaceAdmin)

class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'group', 'course_name')
admin.site.register(Schedule, ScheduleAdmin)

class ScheduleEntryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'schedule', 'num', 'entry_name')
admin.site.register(ScheduleEntry, ScheduleEntryAdmin)

class AlternativePlaceAdmin(admin.ModelAdmin):
    list_display = ('pk', 'schedule_entry', 'name')
admin.site.register(AlternativePlace)
