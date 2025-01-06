from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserGroup, GroupMembership, User
from .serializers import *
from django.shortcuts import get_object_or_404


# 일정 기준
class UserGroupView(APIView):
    def post(self, request, schedule_id, *args, **kwargs):
    
        # Schedule 객체 가져오기
        schedule = get_object_or_404(Schedule, pk=schedule_id)

        # 요청에서 user_id 가져오기
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "User ID is required in the request body."}, status=status.HTTP_400_BAD_REQUEST)

        # User 객체 가져오기
        user = get_object_or_404(User, id=user_id)

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
        
        schedule = get_object_or_404(Schedule, pk=schedule_id)  # Schedule 객체 가져오기

        # Schedule에 연결된 UserGroup 확인
        if not schedule.group:
            return Response({"message": "No UserGroup is associated with this schedule."}, status=status.HTTP_404_NOT_FOUND)

        # UserGroup 정보 직렬화
        group_serializer = UserGroupSerializer(schedule.group)

        # 해당 그룹의 GroupMembership 정보 직렬화
        memberships = GroupMembership.objects.filter(group=schedule.group)
        membership_serializer = GroupMembershipSerializer(memberships, many=True)

        # 결과 반환
        return Response({
            "Group": group_serializer.data,
            "Member": membership_serializer.data
        }, status=status.HTTP_200_OK)



class GroupMembershipView(APIView):
    def post(self, request, group_id, *args, **kwargs):
        
        # 그룹 가져오기
        group = get_object_or_404(UserGroup, pk=group_id)

        # 요청 데이터에서 초대 코드와 사용자 ID 가져오기
        code = request.data.get('code')
        user_id = request.data.get('user_id')

        if not code:
            return Response({"error": "Invitation code is required in the request body."}, status=status.HTTP_400_BAD_REQUEST)
        if not user_id:
            return Response({"error": "User ID is required in the request body."}, status=status.HTTP_400_BAD_REQUEST)

        # 초대 코드 검증
        if group.code != code:
            return Response({"error": "Invalid invitation code for the group."}, status=status.HTTP_400_BAD_REQUEST)

        # 사용자 가져오기
        user = get_object_or_404(User, id=user_id)

        # 사용자가 이미 그룹에 속해 있는지 확인
        if GroupMembership.objects.filter(user=user, group=group).exists():
            return Response({"error": "User is already a member of the group."}, status=status.HTTP_400_BAD_REQUEST)

        # 그룹에 사용자 추가
        GroupMembership.objects.create(user=user, group=group)

        return Response({
            "message": "User successfully added to the group.",
            "group": {
                "id": group.id,
                "code": group.code
            },
            "user": {
                "id": user.id,
                "name": user.name
            }
        }, status=status.HTTP_201_CREATED)


    def delete(self, request, membership_id, *args, **kwargs):
        
        membership = get_object_or_404(GroupMembership, pk=membership_id)  # GroupMembership 객체 가져오기

        # 요청한 사용자가 모임장인지 확인
        user_group = membership.group  # 해당 그룹 가져오기
        requester_membership = GroupMembership.objects.filter(group=user_group, user=request.user).first()

        if not requester_membership or requester_membership.role != "leader":
            return Response({"error": "Only the group leader can remove members."}, status=status.HTTP_403_FORBIDDEN)

        membership.delete()
        return Response({"message": "User removed from group successfully."}, status=status.HTTP_204_NO_CONTENT)

