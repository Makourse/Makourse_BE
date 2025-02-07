from rest_framework import serializers
from course.models import Schedule
from .models import UserGroup, GroupMembership, CustomUser,Notification


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
                "course_name": schedule.course_name
            }
        return None  # 일정이 없는 경우 None 반환

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'email']

class GroupMembershipSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='get_role_display')  # 역할 이름을 읽기 전용 필드로 추가
    user = UserSerializer() # 유저 중첩화(이름&이메일 같이 보여주기 위해)

    class Meta:
        model = GroupMembership
        fields = ['id', 'user', 'role']  # group 필드 제거, role 필드 추가

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id', 'group', 'course_name', 'meet_date_first', 'meet_place', 'latitude', 'longitude']


class NotificationSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.name", read_only=True)
    group_name = serializers.CharField(source="group.schedule.course_name", read_only=True, default="일정 없음")

    class Meta:
        model = Notification
        fields = ["id", "sender", "sender_name", "receiver", "group", "group_name", "notification_type", "content", "created_at", "is_read", "status"]