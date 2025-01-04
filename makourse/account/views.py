from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserGroup, GroupMembership, User
from .serializers import *



class UserGroupView(APIView):
    def post(self, request, schedule_id, *args, **kwargs):
        """
        기존 Schedule에 UserGroup을 등록합니다.
        """
        try:
            # Schedule 객체 가져오기
            schedule = Schedule.objects.get(pk=schedule_id)
        except Schedule.DoesNotExist:
            return Response({"error": "Schedule not found."}, status=status.HTTP_404_NOT_FOUND)

        # 요청에서 user_id 가져오기
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "User ID is required in the request body."}, status=status.HTTP_400_BAD_REQUEST)

        # User 객체 가져오기
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # UserGroup 생성
        serializer = UserGroupSerializer(data=request.data)
        if serializer.is_valid():
            user_group = serializer.save()

            # Schedule과 UserGroup 연결
            schedule.group = user_group
            schedule.save()

            # GroupMembership 추가
            GroupMembership.objects.create(user=user, group=user_group, role="leader")

            return Response({
                "message": "UserGroup registered successfully.",
                "group": serializer.data,
                "schedule": {
                    "id": schedule.id,
                    "course_name": schedule.course_name,
                    "group_code": user_group.code
                }
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, schedule_id, *args, **kwargs):
        """
        특정 Schedule에 연결된 UserGroup을 조회합니다.
        """
        try:
            # Schedule 객체 가져오기
            schedule = Schedule.objects.get(pk=schedule_id)
        except Schedule.DoesNotExist:
            return Response({"error": "Schedule not found."}, status=status.HTTP_404_NOT_FOUND)

        # Schedule에 연결된 UserGroup 확인
        if not schedule.group:
            return Response({"message": "No UserGroup is associated with this schedule."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserGroupSerializer(schedule.group)
        return Response(serializer.data, status=status.HTTP_200_OK)


class JoinGroupView(APIView):
    def post(self, request, *args, **kwargs):
        """
        초대 코드를 통해 그룹에 가입합니다.
        """
        serializer = JoinGroupSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data['code']
            user_id = serializer.validated_data.get('user_id')  # 요청에서 user_id 가져오기

            # 그룹 찾기
            try:
                group = UserGroup.objects.get(code=code)
            except UserGroup.DoesNotExist:
                return Response({"error": "Group not found."}, status=status.HTTP_404_NOT_FOUND)

            # 사용자 찾기
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

            # 사용자가 이미 그룹에 속해 있는지 확인
            if GroupMembership.objects.filter(user=user, group=group).exists():
                return Response({"error": "User is already a member of the group."}, status=status.HTTP_400_BAD_REQUEST)

            # 그룹에 사용자 추가
            GroupMembership.objects.create(user=user, group=group)
            return Response({
                "message": "Successfully joined the group.",
                "group": group.code,
                "user_id": user.id
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class GroupMembershipView(APIView):
    def post(self, request, group_id, *args, **kwargs):
        """
        그룹에 사용자를 추가합니다.
        """
        try:
            group = UserGroup.objects.get(pk=group_id)
        except UserGroup.DoesNotExist:
            return Response({"error": "UserGroup not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['group'] = group.id

        serializer = GroupMembershipSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, group_id, *args, **kwargs):
        """
        특정 그룹에 속한 사용자 목록을 조회합니다.
        """
        try:
            group = UserGroup.objects.get(pk=group_id)
        except UserGroup.DoesNotExist:
            return Response({"error": "UserGroup not found"}, status=status.HTTP_404_NOT_FOUND)

        memberships = GroupMembership.objects.filter(group=group)
        serializer = GroupMembershipSerializer(memberships, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, membership_id, *args, **kwargs):
        """
        특정 GroupMembership 객체를 삭제합니다.
        """
        try:
            membership = GroupMembership.objects.get(pk=membership_id)
        except GroupMembership.DoesNotExist:
            return Response({"error": "Membership not found"}, status=status.HTTP_404_NOT_FOUND)

        # 삭제 제한: 모임원만 삭제 가능
        if membership.role != "member":
            return Response({"error": "Only members can be removed."}, status=status.HTTP_403_FORBIDDEN)

        membership.delete()
        return Response({"message": "User removed from group successfully."}, status=status.HTTP_204_NO_CONTENT)



class GroupScheduleView(APIView):
    def get(self, request, group_id, *args, **kwargs):
        """
        특정 그룹에 연결된 일정을 조회합니다.
        """
        try:
            group = UserGroup.objects.get(pk=group_id)
        except UserGroup.DoesNotExist:
            return Response({"error": "UserGroup not found"}, status=status.HTTP_404_NOT_FOUND)

        schedules = Schedule.objects.filter(group=group)
        serializer = ScheduleSerializer(schedules, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)