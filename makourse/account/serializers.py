from rest_framework import serializers
from course.models import Schedule
from .models import UserGroup, GroupMembership


class UserGroupSerializer(serializers.ModelSerializer):
    schedule = serializers.SerializerMethodField()  # 일정 정보 추가

    class Meta:
        model = UserGroup
        fields = ['id', 'code', 'schedule']  # 일정 필드 포함

    def get_schedule(self, obj):
        
        schedule = getattr(obj, 'schedule', None)  # UserGroup에 연결된 Schedule 가져오기
        if schedule:
            return {
                "id": schedule.id,
                "schedule_name": schedule.course_name
            }
        return None  # 일정이 없는 경우 None 반환

class GroupMembershipSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='get_role_display')  # 역할 이름을 읽기 전용 필드로 추가

    class Meta:
        model = GroupMembership
        fields = ['id', 'user', 'role']  # group 필드 제거, role 필드 추가

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id', 'course_name', 'meet_date_first', 'meet_place']