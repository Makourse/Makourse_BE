from django.contrib import admin
from django.urls import path
from .views import *


urlpatterns = [
    path('schedule/', ScheduleUpdateView.as_view()), # 일정(코스) 등록(post) or 목록 조회(get)
    path('schedule/<int:pk>/', ScheduleUpdateView.as_view()), # 일정(코스) 상세조회(get), 수정(patch), 삭제(delete)
]