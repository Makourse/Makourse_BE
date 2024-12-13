from django.urls import path
from .views import ScheduleEntryView

urlpatterns = [
    path('schedule-entries/post/<int:schedule_id>', ScheduleEntryView.as_view(), name='schedule-entry-create'),  # POST
    path('schedule-entries/<int:pk>', ScheduleEntryView.as_view(), name='schedule-entry-detail'),  # GET, PUT, PATCH, DELETE
]
