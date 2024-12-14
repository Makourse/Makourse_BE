from django.urls import path
from .views import *

urlpatterns = [
    
    # 세부 일정
    path('schedule-entries/post/<int:schedule_id>', ScheduleEntryView.as_view(), name='schedule-entry-create'),  # POST
    path('schedule-entries/<int:pk>', ScheduleEntryView.as_view(), name='schedule-entry-detail'),

    # 대안 장소
    path('schedule-entries/<int:schedule_entry_id>/alternative-places', AlternativePlaceView.as_view(), name='alternative-place-create'),
    path('schedule-entries/<int:schedule_entry_id>/alternative-places/<int:pk>', AlternativePlaceView.as_view(), name='alternative-place-update'),
    path('schedule-entries/<int:schedule_entry_id>/alternative-places/<int:alternative_place_id>/replace', ReplaceWithAlternativePlaceView.as_view(), name='replace-with-alternative-place'),

    path('schedule/', ScheduleUpdateView.as_view()), # 일정(코스) 등록(post) or 목록 조회(get)
    path('schedule/<int:pk>/', ScheduleUpdateView.as_view()), # 일정(코스) 상세조회(get), 수정(patch), 삭제(delete)
]
