from rest_framework import serializers
from .models import *

class ScheduleEntryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleEntry
        fields = '__all__'

class CreateCourseSerializser(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__' 

    # def validate(self, data): # 처음에 날짜만 받을거여서 넣어봤는데 필요한지는 모르겠음
    #     request_method = self.context.get('request').method
    #     if request_method == 'POST':
    #         required_fields = ['meet_date_first', 'meet_date_second','meet_date_third']

class ListCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['pk', 'course_name', 'meet_date_first', 'group']

class ScheduleEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleEntry
        fields = ['pk', 'num', 'entry_name']


class AlternativePlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlternativePlace
        fields = '__all__'
