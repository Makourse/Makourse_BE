from rest_framework import serializers
from .models import *
from django.shortcuts import get_object_or_404
from account.models import *

class CreateMyPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyPlace
        fields = '__all__'

        
class ListMyPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyPlace
        fields = '__all__'


class ScheduleEntryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleEntry
        fields = '__all__'

class CreateCourseSerializser(serializers.ModelSerializer):
    user_id = serializers.CharField(write_only=True)  # 요청에서 유저 ID (id 필드) 처리

    class Meta:
        model = Schedule
        fields = [
            'meet_date_first', 'meet_date_second', 'meet_date_third',
            'course_name', 'meet_place', 'latitude', 'longitude', 'user_id'
        ]

    def create(self, validated_data):
        # user_id로 User 객체 가져오기
        user_id = validated_data.pop('user_id')  # 요청 데이터에서 user_id 추출
        user = get_object_or_404(User, id=user_id)  # User 모델의 id 필드로 조회

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
