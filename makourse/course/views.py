from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .serializers import *
from .models import *
from rest_framework.response import Response
from rest_framework.decorators import APIView

class MyPlaceView(APIView):
    def post(self, request, *args, **kwargs):
        request.data['user'] = User.objects.get(id="test").id
        # 일단 user_id를 "test"로 고정 (로그인 구현 전 테스트용)
        serializer = CreateMyPlaceSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def get(self, request, *args, **kwargs):
        my_place = MyPlace.objects.all()
        serializer = ListMyPlaceSerializer(my_place, many=True)
        return Response(serializer.data, status=200)

    def delete(self, request, pk, *args, **kwargs):
        my_place = get_object_or_404(MyPlace, pk=pk)
        my_place.delete()

        return Response({"message":"My place deleted"}, status=204)