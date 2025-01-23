import requests
import os
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import *
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from .serializers import *
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from urllib.parse import unquote
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from urllib.parse import urlparse

# 1. Authorization code 받아오기(프론트가 소셜에서)
# 2. Authorizaiton code를 가지고 서버가 소셜에게 Access Token 요청
# 3. 서버는 받은 Access Token으로 user info 요청

User = get_user_model()

class SocialLoginAPIView(APIView):
    # 소셜로그인은 인증없이 접근 가능해야함
    permission_classes = [AllowAny]  # 인증 없이 접근 허용
    
    def get(self, request, provider):
        # GET으로 전달된 Authorization Code 처리
        code = request.GET.get('code')
        if not code:
            return Response({'error': 'Authorization code is required'}, status=400)

        # POST 로직 재사용
        return self.post(request, provider)


    @swagger_auto_schema(
        tags=['유저'],
        operation_summary="소셜 로그인",
        operation_description="Authorization code를 통해 로그인하고 JWT token을 반환합니다.",
        responses={200: "JWT Token with user info", 400: "Error message"},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'code': openapi.Schema(type=openapi.TYPE_STRING, description='Authorization code from the front end')
            },
            required=['code']
        )
    )
    def post(self, request, provider):
        code = request.data.get('code') # 프론트에서 전달한 Authorization Code
        if not code:
            return Response({'error': 'Authorization code is required'}, status=400)

        # 소셜 키와 리디렉션 URI 가져오기
        social_keys = settings.SOCIAL_KEYS.get(provider)
        if not social_keys:
            return Response({'error': f'{provider} is not a supported provider'}, status=400)


        # 적절한 리디렉션 URI 선택 (0: 프론트 배포 도메인, 1: 로컬, 2: 백엔드 배포 도메인)
        address = request.data.get('address')
        redirect_uris = settings.SOCIAL_REDIRECT_URIS.get(provider, [])
        redirect_uri = redirect_uris[address]

        #print("Redirect URI:", redirect_uri) # 코트 확인
        
        if not redirect_uri:
            return Response({'error': 'No valid redirect URI found'}, status=400)


        # Access Token 요청 (by using authorization code)
        token_data = self.get_access_token(provider, code, social_keys, redirect_uri)
        if 'error' in token_data:
            return Response({'error': token_data['error']}, status=400)


        # 사용자 정보 요청
        user_info = self.get_user_info(provider, token_data['access_token'])
        if 'error' in user_info:
            return Response({'error': user_info['error']}, status=400)
        
        # 사용자 생성 또는 업데이트
        user, created = User.objects.get_or_create(
            email=user_info['email'],  # 이메일 기반으로 사용자 구분
            defaults={
                'name': user_info['name'],
                'social_provider': provider,
                'profile_image': 'user_photo/default.png',  # 새 사용자에게만 기본값 설정
            }        
        )

        # 사용자 업데이트 (이미 회원인 경우)
        if not created:
            if not user.name and user_info.get('name'):
                user.name = user_info['name']
            user.social_provider = provider  # 소셜 제공자 정보 업데이트
            user.is_logged_in = True
            user.save()

        # JWT 발급
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
            },
            'is_new': created
            
        })


    # access token 요청하기
    def get_access_token(self, provider, code, social_keys, redirect_uri):
        token_url = {
            'google': "https://oauth2.googleapis.com/token",
            'naver': "https://nid.naver.com/oauth2.0/token",
            'kakao': "https://kauth.kakao.com/oauth/token",
        }.get(provider)
        # URL 인코딩 처리
        decoded_code = unquote(code)
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': social_keys['client_id'],
            'client_secret': social_keys.get('client_secret', ''),
            'code': decoded_code,
            'redirect_uri': redirect_uri,
        }
        response = requests.post(token_url, data=token_data)
        if response.status_code == 200:
            return response.json() # access token 반환
        print("Access Token Error:", response.json())
        return {'error': f'Failed to fetch {provider} access token'}


    # 사용자 정보 요청하기 (by using access_token)
    def get_user_info(self, provider, access_token):
        # 소셜 로그인 제공자의 사용자 정보 URL과 헤더 구성
        user_info_url = {
            'google': "https://www.googleapis.com/oauth2/v1/userinfo",
            'naver': "https://openapi.naver.com/v1/nid/me",
            'kakao': "https://kapi.kakao.com/v2/user/me",
        }.get(provider)

        headers = {'Authorization': f'Bearer {access_token}'}
        # 사용자 정보 요청
        response = requests.get(user_info_url, headers=headers)

        if response.status_code != 200:
            return {'error': f'Failed to fetch {provider} user info'}

        data = response.json() # user info

        # 플랫폼별로 사용자 정보 정리
        # 네이버: resopnse 안에 사용자 info 담겨있음
        # 카카오: kakao_account 안에 사용자 info 담겨있음
        # 구글: 중첩 X
        if provider == 'naver':
            data = data.get('response', {})
        elif provider == 'kakao':
            data = data.get('kakao_account', {})

        return {
            'email': data.get('email'),
            'name': data.get('name') if provider != 'kakao' else data.get('profile', {}).get('nickname')
        } # 카카오는 이름이 nickname이라는 필드에 담겨 있음


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['유저'],
        operation_summary="로그아웃",
        operation_description="로그아웃하면 유저의 `is_logged_in`는 false가 됩니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='The refresh token used for logging out.')
            },
            required=['refresh']
        ),
        responses={
            200: openapi.Response(description="User logged out successfully."),
            400: openapi.Response(description="Error message (e.g., invalid token or missing refresh token).")
        }
    )
    def post(self, request):
       refresh_token = request.data.get('refresh')  # Refresh Token 받기
       if not refresh_token:
            return Response({'error': 'Refresh token is required'}, status=400)

       try:
            # Refresh Token에서 사용자 정보 추출
            token = RefreshToken(refresh_token)
            user_id = token['user_id']  # 토큰에서 사용자 ID 추출

            # 사용자 객체 가져오기
            user = get_object_or_404(User, id=user_id)

            # 사용자 상태 업데이트 (is_logged_in = False)
            user.is_logged_in = False
            user.save()

           # 블랙리스트에 추가
            token.blacklist()

            return Response({'message': 'Logged out successfully'}, status=200)
       except Exception as e:
            return Response({'error': str(e)}, status=400)


class ProfileImageUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # 프로필 이미지 업로드 및 수정
    @swagger_auto_schema(
        tags=['유저'],
        operation_summary="프로필 사진 업로드",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'profile_image': openapi.Schema(type=openapi.TYPE_FILE, description='The new profile image file.')
            },
            required=['profile_image']
        ),
        responses={
            200: openapi.Response(description="Profile image updated successfully.", schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
                    'profile_image': openapi.Schema(type=openapi.TYPE_STRING, description='URL of the updated profile image')
                }
            )),
            400: openapi.Response(description="Error message (e.g., no image file provided).")
        }
    )
    def post(self, request):
        # 현재 로그인된 사용자 가져오기
        user = request.user

        # 업로드된 파일 가져오기
        profile_image = request.FILES.get('profile_image')
        if not profile_image:
            return Response({'error': 'No image file provided'}, status=400)
        
        # 현재 프로필 이미지가 default가 아닌 경우 삭제
        if user.profile_image.name != 'user_photo/default.png':
            profile_image_path = os.path.join(settings.MEDIA_ROOT, user.profile_image.name)
            if os.path.exists(profile_image_path):
                os.remove(profile_image_path)  # 파일 삭제

        # 사용자 프로필 이미지 업데이트
        user.profile_image = profile_image
        user.save()

        return Response({'message': 'Profile image updated successfully', 'profile_image': user.profile_image.url})


# 프로필 사진 기본 이미지로
class ResetProfileImageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['유저'],
        operation_summary="기본 프로필로 reset",
        responses={
            200: openapi.Response(description="Profile image reset to default.", schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
                    'profile_image': openapi.Schema(type=openapi.TYPE_STRING, description='URL of the default profile image')
                }
            )),
            400: openapi.Response(description="Error message if something goes wrong.")
        }
    )
    def post(self, request):
        user = request.user

        # 현재 프로필 이미지가 default가 아닌 경우 삭제
        if user.profile_image.name != 'user_photo/default.png':  # 현재 프로필이 기본 이미지가 아닌 경우
            profile_image_path = os.path.join(settings.MEDIA_ROOT, user.profile_image.name)
            if os.path.exists(profile_image_path):
                os.remove(profile_image_path)  # 파일 삭제

        # 프로필 이미지를 기본 이미지로 설정
        user.profile_image = 'user_photo/default.png'
        user.save()

        return Response({'message': 'Profile image reset to default', 'profile_image': user.profile_image.url})
        # 일정 기준

class UserSchedulesView(APIView):
    @swagger_auto_schema(
        tags=['일정(코스)'],
        operation_summary="해당 유저의 정보 및 일정 목록 조회",
        responses={
            200: openapi.Response(description="List of user schedules.", schema=ScheduleSerializer),
            404: openapi.Response(description="User not found.")
        }
    )
    def get(self, request, user_pk, *args, **kwargs):
        user = get_object_or_404(CustomUser, pk=user_pk)
        group_memberships = GroupMembership.objects.filter(user=user)
        schedules = Schedule.objects.filter(group__in=[membership.group for membership in group_memberships]).distinct()

        serializer = ScheduleSerializer(schedules, many=True)

        user_data = {
            "id": user.id,
            "email": user.email,
            "profile_image": user.profile_image.url,
            "name": user.name,
            "social_provider": user.social_provider,
            "is_logged_in": user.is_logged_in
        }

        response_data = {
            "user": user_data,
            "schedules": serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)


# 그룹
class UserGroupView(APIView):
    #permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['그룹'],
        operation_summary="그룹 생성",
        operation_description="유저가 일정을 생성하면 자동적으로 그룹이 생성됩니다.",
        request_body=UserGroupSerializer,
        responses={201: UserGroupSerializer, 400: "Validation Error"}
    )
    def post(self, request, schedule_id, *args, **kwargs):
    
        # Schedule 객체 가져오기
        schedule = get_object_or_404(Schedule, pk=schedule_id)

        # 요청에서 user_id 가져오기
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "User ID is required in the request body."}, status=status.HTTP_400_BAD_REQUEST)

        # User 객체 가져오기
        user = get_object_or_404(CustomUser, id=user_id)

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


    @swagger_auto_schema(
        tags=['그룹'],
        operation_summary="그룹 조회",
        operation_description="해당 일정의 그룹 멤버들을 조회합니다..",
        responses={200: "User Group and Members Info", 404: "Group not found"}
    )
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



class GroupMembershipJoinView(APIView):
    @swagger_auto_schema(
        tags=['그룹'],
        operation_summary="초대된 유저 그룹에 추가",
        operation_description="특정 일정에 초대된 그룹 코드로 유저를 그룹에 추가합니다",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'code': openapi.Schema(type=openapi.TYPE_STRING, description='Invitation code'),
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID to add to group'),
            },
            required=['code', 'user_id']
        ),
        responses={201: "User added to group", 400: "Error message"}
    )
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
        user = get_object_or_404(CustomUser, id=user_id)

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



class GroupMembershipDeleteView(APIView):
    @swagger_auto_schema(
        tags=['그룹'],
        operation_summary="유저 그룹에서 내보내기",
        operation_description="그룹의 리더가 멤버를 내보냅니다.",
        responses={204: "User removed from group", 400: "Error message"}
    )
    def delete(self, request, membership_id, *args, **kwargs):
        
        membership = get_object_or_404(GroupMembership, pk=membership_id)  # GroupMembership 객체 가져오기

        user_group = membership.group  # 해당 그룹 가져오기
        requester_user = membership.user  # membership 객체에서 사용자 가져오기
        requester_membership = GroupMembership.objects.filter(group=user_group, user=requester_user).first()

        # if not requester_membership or requester_membership.role != "leader":
        #     return Response({"error": "Only the group leader can remove members."}, status=status.HTTP_403_FORBIDDEN)

        membership.delete()
        return Response({"message": "User removed from group successfully."}, status=status.HTTP_204_NO_CONTENT)

