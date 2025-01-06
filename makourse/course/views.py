from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *

from django.shortcuts import get_object_or_404
from .serializers import *
from .models import *
from rest_framework.response import Response
from rest_framework.decorators import APIView

# 나만의 장소 기능
class MyPlaceView(APIView):
    # 나만의 장소 추가
    def post(self, request, *args, **kwargs):
        request.data['user'] = User.objects.get(id="test").id
        # 일단 user_id를 "test"로 고정 (로그인 구현 전 테스트용)
        serializer = CreateMyPlaceSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


    # 나만의 장소 목록 조회
    def get(self, request, *args, **kwargs):
        my_place = MyPlace.objects.all()
        serializer = ListMyPlaceSerializer(my_place, many=True)
        return Response(serializer.data, status=200)


    # 나만의 장소 삭제
    def delete(self, request, pk, *args, **kwargs):
        my_place = get_object_or_404(MyPlace, pk=pk)
        my_place.delete()

        return Response({"message":"My place deleted"}, status=204)


    # 나만의 장소 수정
    def patch(self, request, pk, *args, **kwargs):
        my_place = get_object_or_404(MyPlace, pk=pk)
        serializer = CreateMyPlaceSerializer(my_place, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)



class ScheduleEntryView(APIView):

    def post(self, request, schedule_id, *args, **kwargs):

        schedule = get_object_or_404(Schedule, pk=schedule_id)

        data = request.data.copy()
        data["schedule"] = schedule.id

        serializer = ScheduleEntryDetailSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request, pk, *args, **kwargs):
        
        schedule_entry = get_object_or_404(ScheduleEntry, pk=pk)  # ScheduleEntry 객체 가져오기

        serializer = ScheduleEntryDetailSerializer(schedule_entry)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk, *args, **kwargs):
        
        schedule_entry = get_object_or_404(ScheduleEntry, pk=pk)  # ScheduleEntry 객체 가져오기

        serializer = ScheduleEntryDetailSerializer(schedule_entry, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        
        schedule_entry = get_object_or_404(ScheduleEntry, pk=pk)  # ScheduleEntry 객체 가져오기

        schedule_entry.delete()
        return Response({"message": "ScheduleEntry deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class AlternativePlaceView(APIView):
    def post(self, request, schedule_entry_id, *args, **kwargs):

        schedule_entry = get_object_or_404(ScheduleEntry, pk=schedule_entry_id)  # ScheduleEntry 객체 가져오기

        data = request.data.copy()
        data['schedule_entry'] = schedule_entry.id  

        serializer = AlternativePlaceSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, schedule_entry_id, *args, **kwargs):

        schedule_entry = get_object_or_404(ScheduleEntry, pk=schedule_entry_id)  # ScheduleEntry 객체 가져오기

        alternative_places = AlternativePlace.objects.filter(schedule_entry=schedule_entry)
        serializer = AlternativePlaceSerializer(alternative_places, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk, *args, **kwargs):
      
        alternative_place = get_object_or_404(AlternativePlace, pk=pk)  # AlternativePlace 객체 가져오기

        alternative_place.delete()
        return Response({"message": "AlternativePlace deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk, *args, **kwargs):
        
        alternative_place = get_object_or_404(AlternativePlace, pk=pk)  # AlternativePlace 객체 가져오기

        serializer = AlternativePlaceSerializer(alternative_place, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReplaceWithAlternativePlaceView(APIView):
    def put(self, request, alternative_place_id, *args, **kwargs):
   
        alternative_place = get_object_or_404(AlternativePlace, pk=alternative_place_id)  # AlternativePlace 객체 가져오기
        schedule_entry = alternative_place.schedule_entry  # 연결된 ScheduleEntry 가져오기

        updated_data = {
            "address": alternative_place.address,
            "latitude": alternative_place.latitude,
            "longitude": alternative_place.longitude,
            "category": alternative_place.category,
            "entry_name": alternative_place.name,
        }

        serializer = ScheduleEntryDetailSerializer(schedule_entry, data=updated_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# 일정(코스) 등록 및 수정
class ScheduleUpdateView(APIView):
    # 일정 등록
    def post(self, request, *args, **kwargs):
        serializer = CreateCourseSerializser(data=request.data, context={'request':request})
       
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


    # 일정 수정
    def patch(self, request, pk, *args, **kwargs):
        schedule = get_object_or_404(Schedule, pk=pk)
        serializer = CreateCourseSerializser(schedule, data=request.data, partial=True, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


    # 일정 조회
    def get(self, request, pk=None, *args, **kwargs):
        if pk: # 특정일정 상세조회
            schedule = get_object_or_404(Schedule, pk=pk)
            serializer = CreateCourseSerializser(schedule)

            schedule_entry = ScheduleEntry.objects.filter(schedule=pk)
            entry_serializer = ScheduleEntrySerializer(schedule_entry, many=True)
            return Response({'course':serializer.data, 'entry':entry_serializer.data}, status=200)
        else: # 일정 목록 조회
            schedules = Schedule.objects.all()
            serializer = ListCourseSerializer(schedules, many=True)
            
            return Response(serializer.data, status=200)


    # 일정 삭제
    def delete(self, request, pk, *args, **kwargs):
        schedule = get_object_or_404(Schedule, pk=pk)
        schedule.delete()
        
        return Response({"message": "Schdeule deleted"}, status=204)
