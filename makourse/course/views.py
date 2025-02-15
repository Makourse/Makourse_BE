from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import APIView
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated

# 나만의 장소 기능
class MyPlaceView(APIView):
    # permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    # 나만의 장소 추가
    @swagger_auto_schema( 
        tags=["나만의 장소"],
        operation_summary="나만의 장소 추가",
        request_body = CreateMyPlaceSerializer,
        responses={
            201: openapi.Response('Place created successfully', CreateMyPlaceSerializer),
            400: openapi.Response('Validation error'),
        }
    )
    def post(self, request, pk, *args, **kwargs):
        request.data['user'] = pk
        # request.user.id
        # 일단 url로 user pk 받기
        serializer = CreateMyPlaceSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


    # 나만의 장소 목록 조회
    @swagger_auto_schema( 
        tags=["나만의 장소"],
        operation_summary="나만의 장소 목록 조회",
        responses={200: ListMyPlaceSerializer(many=True)}
    )
    def get(self, request, pk, *args, **kwargs):
        my_places = MyPlace.objects.filter(user=pk)
        serializer = ListMyPlaceSerializer(my_places, many=True)
        return Response(serializer.data, status=200)

 

# 나만의 장소 기능
class MyPlaceDetailView(APIView):
    # permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    # 나만의 장소 삭제
    @swagger_auto_schema(
        tags=["나만의 장소"],
        operation_summary="나만의 장소 삭제",
        responses={204: openapi.Response("Place deleted successfully")},
    )
    def delete(self, request, myplace_id, *args, **kwargs):
        my_place = get_object_or_404(MyPlace, pk=myplace_id) # user=request.user 넣기
        my_place.delete()

        return Response({"message":"My place deleted"}, status=204)


    # 나만의 장소 수정
    @swagger_auto_schema(
        tags=["나만의 장소"],
        operation_summary="나만의 장소 수정",
        request_body=CreateMyPlaceSerializer,
        responses={
            201: openapi.Response("Place updated successfully", CreateMyPlaceSerializer),
            400: openapi.Response("Validation error"),
        },
    )
    def patch(self, request, myplace_id, *args, **kwargs):
        my_place = get_object_or_404(MyPlace, pk=myplace_id) # user=request.user 넣기
        serializer = CreateMyPlaceSerializer(my_place, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
        

# 스케줄 속 각 일정
class ScheduleEntryView(APIView):
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["스케줄 속 각 일정"],
        operation_summary="스케줄 속 각 일정 추가하기",
        request_body=ScheduleEntryDetailSerializer,
        responses={201: ScheduleEntryDetailSerializer, 400: "Validation Error"}
    )
    def post(self, request, schedule_id, *args, **kwargs):
        schedule = get_object_or_404(Schedule, pk=schedule_id)

        data = request.data.copy()
        data["schedule"] = schedule.id

        serializer = ScheduleEntryDetailSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 스케줄 속 각 일정
class ScheduleEntryDetailView(APIView):
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["스케줄 속 각 일정"],
        operation_summary="각 일정 조회",
        responses={200: ScheduleEntryDetailSerializer, 404: "Not Found"}
    )
    def get(self, request, pk, *args, **kwargs):
        
        schedule_entry = get_object_or_404(ScheduleEntry, pk=pk) # user=request.user 넣기
        # ScheduleEntry 객체 가져오기

        serializer = ScheduleEntryDetailSerializer(schedule_entry)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @swagger_auto_schema(
        tags=["스케줄 속 각 일정"],
        operation_summary="스케줄 속 각 일정 수정하기",
        request_body=ScheduleEntryDetailSerializer,
        responses={200: ScheduleEntryDetailSerializer, 400: "Validation Error"}
    )
    def patch(self, request, pk, *args, **kwargs):
        
        schedule_entry = get_object_or_404(ScheduleEntry, pk=pk)
        # ScheduleEntry 객체 가져오기

        serializer = ScheduleEntryDetailSerializer(schedule_entry, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        tags=["스케줄 속 각 일정"],
        operation_summary="스케줄 속 각 일정 삭제하기",
        responses={204: "ScheduleEntry deleted successfully."}
    )
    def delete(self, request, pk, *args, **kwargs):
        schedule_entry = get_object_or_404(ScheduleEntry, pk=pk)
        # ScheduleEntry 객체 가져오기

        schedule_entry.delete()
        return Response({"message": "ScheduleEntry deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# 대안 장소
class AlternativePlaceView(APIView):
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["대안장소"],
        operation_summary="대안장소 추가하기",
        request_body=AlternativePlaceSerializer,
        responses={201: AlternativePlaceSerializer, 400: "Validation Error"}
    )
    def post(self, request, schedule_entry_id, *args, **kwargs):

        schedule_entry = get_object_or_404(ScheduleEntry, pk=schedule_entry_id)
        # ScheduleEntry 객체 가져오기

        data = request.data.copy()
        data['schedule_entry'] = schedule_entry.id  

        serializer = AlternativePlaceSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    

    @swagger_auto_schema(
        tags=["대안장소"],
        operation_summary="대안장소 조회하기",
        responses={200: AlternativePlaceSerializer(many=True)}
    )
    def get(self, request, schedule_entry_id, *args, **kwargs):

        schedule_entry = get_object_or_404(ScheduleEntry, pk=schedule_entry_id)
        # ScheduleEntry 객체 가져오기

        alternative_places = AlternativePlace.objects.filter(schedule_entry=schedule_entry)
        serializer = AlternativePlaceSerializer(alternative_places, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 대안 장소
class AlternativePlaceDetailView(APIView):
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["대안장소"],
        operation_summary="대안장소 삭제하기",
        responses={204: "Deleted Successfully"}
    )
    def delete(self, request, pk, *args, **kwargs):
      
        alternative_place = get_object_or_404(AlternativePlace, pk=pk)  # AlternativePlace 객체 가져오기

        alternative_place.delete()
        return Response({"message": "AlternativePlace deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


    @swagger_auto_schema(
        tags=["대안장소"],
        operation_summary="대안장소 수정하기",
        responses={200: AlternativePlaceSerializer, 400: "Validation Error"}

    )
    def patch(self, request, pk, *args, **kwargs):
        
        alternative_place = get_object_or_404(AlternativePlace, pk=pk)  # AlternativePlace 객체 가져오기

        serializer = AlternativePlaceSerializer(alternative_place, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 대안 장소로 대체
class ReplaceWithAlternativePlaceView(APIView):
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["대안장소"],
        operation_summary="일정을 대안장소로 대체",
        responses={200: ScheduleEntryDetailSerializer, 400: "Validation Error"}
    )
    def put(self, request, alternative_place_id, *args, **kwargs):
   
        alternative_place = get_object_or_404(AlternativePlace, pk=alternative_place_id)  # AlternativePlace 객체 가져오기
        schedule_entry = alternative_place.schedule_entry  # 연결된 ScheduleEntry 가져오기

        updated_data = {
            "address": alternative_place.address,
            "latitude": alternative_place.latitude,
            "longitude": alternative_place.longitude,
            "category": alternative_place.category,
            "entry_name": alternative_place.name,
            "content": alternative_place.content,  
            "open_time": alternative_place.open_time, 
            "close_time": alternative_place.close_time,  
        }

        serializer = ScheduleEntryDetailSerializer(schedule_entry, data=updated_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


# 일정(코스) 등록 및 수정
class ScheduleUpdateView(APIView):
    #permission_classes = [IsAuthenticated]

    # 일정 등록
    @swagger_auto_schema(
        tags=["일정(코스)"],
        operation_summary="일정(코스) 생성",
        request_body=CreateCourseSerializer,
        responses={201: CreateCourseSerializer, 400: "Validation Error"}
    )
    def post(self, request, *args, **kwargs):
    
        serializer = CreateCourseSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 일정(코스) 수정, 조회, 삭제
class ScheduleDetailView(APIView):
    #permission_classes = [IsAuthenticated]

    # 일정 수정
    @swagger_auto_schema(
        tags=["일정(코스)"],
        operation_summary="일정 수정",
        request_body=CreateCourseSerializer,
        responses={200: CreateCourseSerializer, 400: "Validation Error"}
    )
    def patch(self, request, schedule_id, *args, **kwargs):
        schedule = get_object_or_404(Schedule, pk=schedule_id)
        serializer = CreateCourseSerializer(schedule, data=request.data, partial=True, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


    # 일정 조회
    @swagger_auto_schema(
        tags=["일정(코스)"],
        operation_summary="일정 상세 조회",
        operation_description="url에 일정 pk를 넣으면 해당 일정 상세가 조회됩니다.",
        responses={200: "Schedule List or Detail"}
    )
    def get(self, request, schedule_id, *args, **kwargs):
        # 특정일정 상세조회
        schedule = get_object_or_404(Schedule, pk=schedule_id)
        serializer = CreateCourseSerializer(schedule)

        schedule_entry = ScheduleEntry.objects.filter(schedule=schedule_id)
        entry_serializer = ScheduleEntrySerializer(schedule_entry, many=True)
        return Response({'course':serializer.data, 'entry':entry_serializer.data}, status=200)
        # else: # 일정 목록 조회
        #     schedules = Schedule.objects.filter()
        #     serializer = ListCourseSerializer(schedules, many=True)
            
        #     return Response(serializer.data, status=200)


    # 일정 삭제
    @swagger_auto_schema(
        tags=["일정(코스)"],
        operation_summary="일정 삭제",
        responses={204: "Deleted Successfully"}
    )
    def delete(self, request, schedule_id, *args, **kwargs):
        schedule = get_object_or_404(Schedule, pk=schedule_id)
        schedule.delete()
        
        return Response({"message": "Schdeule deleted"}, status=204)

from django.http import JsonResponse

def test_api(request):
    return JsonResponse({
        "status": "success",
        "message": "Test API is working correctly!"
    })