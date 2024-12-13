from django.contrib import admin
from django.urls import path
from .views import *


urlpatterns = [
    path('myplace/', MyPlaceView.as_view()), # 나만의 장소 추가(post), 목록조회(get)
    path('myplace/<int:pk>/', MyPlaceView.as_view()) # 나만의 장소 삭제(delete)
]