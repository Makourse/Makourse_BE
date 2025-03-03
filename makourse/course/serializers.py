from rest_framework import serializers
from .models import *
from django.shortcuts import get_object_or_404
from account.models import *

class CreateMyPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyPlace
        fields = ['id', 'place_name', 'address', 'latitude', 'longitude', 'content'] 


        
class ListMyPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyPlace
        fields = '__all__'


class ScheduleEntryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleEntry
        fields = '__all__'

class ScheduleEntryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleEntry
        fields = '__all__'


class CreateCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'  # 모든 필드 포함

    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("유효한 사용자 정보를 찾을 수 없습니다.")

        user = request.user  # request.user 사용

        # 일정 생성
        schedule = Schedule.objects.create(**validated_data)

        # UserGroup 생성
        user_group = UserGroup.objects.create()

        # 일정과 UserGroup 연결
        schedule.group = user_group
        schedule.save()

        # 그룹에 모임장 추가
        GroupMembership.objects.create(user=user, group=user_group, role="leader")

        return schedule

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
