from django.urls import path
from .views import *

urlpatterns = [
    path('myplace/<int:pk>', MyPlaceView.as_view()), # 나만의 장소 추가(post), 목록조회(get)
    path('myplace/<int:myplace_id>/', MyPlaceDetailView.as_view()), # 나만의 장소 삭제(delete), 수정(patch)
    
    # 세부 일정
    path('schedule-entries/post/<int:schedule_id>', ScheduleEntryView.as_view(), name='schedule-entry-create'),  # POST
    path('schedule-entries/<int:pk>', ScheduleEntryDetailView.as_view(), name='schedule-entry-detail'),

    # 대안 장소
    path('schedule-entries/<int:schedule_entry_id>/alternative-places', AlternativePlaceView.as_view(), name='alternative-place-create'),
    path('schedule-entries/<int:schedule_entry_id>/alternative-places/<int:pk>', AlternativePlaceDetailView.as_view(), name='alternative-place-update'),
    path('schedule-entries/<int:schedule_entry_id>/alternative-places/<int:alternative_place_id>/replace', ReplaceWithAlternativePlaceView.as_view(), name='replace-with-alternative-place'),

    # 일정(코스)
    path('schedule/', ScheduleUpdateView.as_view()), # 일정(코스) 등록(post)
    path('schedule/<int:schedule_id>/', ScheduleDetailView.as_view()), # 일정(코스) 상세조회(get), 수정(patch), 삭제(delete)
]
