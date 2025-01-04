from rest_framework import serializers
from course.models import Schedule
from .models import UserGroup, GroupMembership, User

class JoinGroupSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=30)  # 초대 코드
    user_id = serializers.CharField(max_length=100)  # 사용자 ID 추가

    def validate_code(self, value):
        if not UserGroup.objects.filter(code=value).exists():
            raise serializers.ValidationError("Invalid invitation code.")
        return value

    def validate_user_id(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User ID does not exist.")
        return value


class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroup
        fields = ['id', 'code']

class GroupMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMembership
        fields = ['id', 'user', 'group']

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id', 'course_name', 'meet_date_first', 'meet_place']