from django.contrib import admin
from .models import *

class MyPlaceAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'place_name')
admin.site.register(MyPlace, MyPlaceAdmin)

class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'group', 'course_name')
admin.site.register(Schedule, ScheduleAdmin)

class ScheduleEntryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'get_schedule', 'num', 'get_entry_name')  

    def get_schedule(self, obj):
        return obj.schedule if obj.schedule else "N/A" 
    get_schedule.short_description = "Schedule"

    def get_entry_name(self, obj):
        return obj.entry_name if obj.entry_name else "N/A"  
    get_entry_name.short_description = "Entry Name"

admin.site.register(ScheduleEntry, ScheduleEntryAdmin)


class AlternativePlaceAdmin(admin.ModelAdmin):
    list_display = ('pk', 'schedule_entry', 'name')
admin.site.register(AlternativePlace)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'receiver', 'sender', 'notification_type', 'group', 'content', 'created_at', 'is_read', 'status')
    list_filter = ('notification_type', 'is_read', 'status', 'created_at')
    search_fields = ('receiver__email', 'sender__email', 'content')
    ordering = ('-created_at',)
    fieldsets = (
        ('알림 정보', {
            'fields': ('receiver', 'sender', 'notification_type', 'group', 'content', 'is_read', 'status')
        }),
        ('추가 정보', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ('created_at',)  # 생성된 날짜는 읽기 전용
