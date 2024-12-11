from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Schedule, ScheduleEntry
from .serializers import ScheduleEntrySerializer


class ScheduleEntryView(APIView):

    def post(self, request, schedule_id, *args, **kwargs):

        try:
            schedule = Schedule.objects.get(pk=schedule_id)
        except Schedule.DoesNotExist:
            return Response({"error": "Schedule not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data["schedule"] = schedule.id

        serializer = ScheduleEntrySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk, *args, **kwargs):

        try:
            schedule_entry = ScheduleEntry.objects.get(pk=pk)
        except ScheduleEntry.DoesNotExist:
            return Response({"error": "ScheduleEntry not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ScheduleEntrySerializer(schedule_entry)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):

        try:
            schedule_entry = ScheduleEntry.objects.get(pk=pk)
        except ScheduleEntry.DoesNotExist:
            return Response({"error": "ScheduleEntry not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ScheduleEntrySerializer(schedule_entry, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):

        try:
            schedule_entry = ScheduleEntry.objects.get(pk=pk)
        except ScheduleEntry.DoesNotExist:
            return Response({"error": "ScheduleEntry not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ScheduleEntrySerializer(schedule_entry, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):

        try:
            schedule_entry = ScheduleEntry.objects.get(pk=pk)
        except ScheduleEntry.DoesNotExist:
            return Response({"error": "ScheduleEntry not found"}, status=status.HTTP_404_NOT_FOUND)

        schedule_entry.delete()
        return Response({"message": "ScheduleEntry deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
