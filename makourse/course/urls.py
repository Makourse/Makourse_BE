from django.urls import path
from .views import *

urlpatterns = [
    path('schedule-entries/post/<int:schedule_id>', ScheduleEntryView.as_view(), name='schedule-entry-create'),  # POST
    path('schedule-entries/<int:pk>', ScheduleEntryView.as_view(), name='schedule-entry-detail'),  # GET, PUT, PATCH, DELETE
    path('schedule/', ScheduleUpdateView.as_view()), # 일정(코스) 등록(post) or 목록 조회(get)
    path('schedule/<int:pk>/', ScheduleUpdateView.as_view()), # 일정(코스) 상세조회(get), 수정(patch), 삭제(delete)
]
