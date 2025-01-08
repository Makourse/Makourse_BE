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

    def post(self, request, provider):
        code = request.data.get('code') # 프론트에서 전달한 Authorization Code
        if not code:
            return Response({'error': 'Authorization code is required'}, status=400)

        # 소셜 키와 리디렉션 URI 가져오기
        social_keys = settings.SOCIAL_KEYS.get(provider)
        redirect_uri = settings.SOCIAL_REDIRECT_URIS.get(provider)

        if not social_keys or not redirect_uri:
            return Response({'error': f'{provider} is not a supported provider'}, status=400)

        
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
            }
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

    def post(self, request):
        # 현재 로그인된 사용자 가져오기
        user = request.user

        # 업로드된 파일 가져오기
        profile_image = request.FILES.get('profile_image')
        if not profile_image:
            return Response({'error': 'No image file provided'}, status=400)

        # 사용자 프로필 이미지 업데이트
        user.profile_image = profile_image
        user.save()

        return Response({'message': 'Profile image updated successfully', 'profile_image': user.profile_image.url})

class ResetProfileImageAPIView(APIView):
    permission_classes = [IsAuthenticated]

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


# 그룹
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

