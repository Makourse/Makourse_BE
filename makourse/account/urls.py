from django.urls import path
from .views import *


urlpatterns = [
    path('<str:provider>/login/', SocialLoginAPIView.as_view(), name='social-login'), # 소셜 로그인
    path('<str:provider>/callback/', SocialLoginAPIView.as_view(), name='social-login-redirect'), # 소셜 로그인
    path('logout/', LogoutAPIView.as_view(), name='logout'), # 로그아웃
    path('profile/update', ProfileAPIView.as_view(), name='profile-update'), # 프로필 수정 (patch)
    path('profile/image-reset', ProfileAPIView.as_view(), name='profile-image-reset'), # 프로필 기본 이미지로 변경 (post)
    path('profile', ProfileAPIView.as_view(), name='profile'), # 유저정보(프로필 사진 포함)

    # 유저에 따른 schedule 정보 보기
    path('schedules', UserSchedulesView.as_view(), name='user-schedules'),
    
    # 그룹 보기
    path('schedules/<int:schedule_id>/group', UserGroupView.as_view(), name='schedule-group'),
    path('groups/<int:group_id>/join', GroupMembershipJoinView.as_view(), name='group-join'), # 그룹원 등록
    path('groups/<int:group_id>/members/<int:membership_id>', GroupMembershipDeleteView.as_view(), name='group-member-delete'), # 그룹원 삭제

    # 초대 알림
    path('groups/<int:group_id>/invite', GroupMembershipInviteView.as_view(), name='group-invite'), # 그룹원 초대
    path('groups/<int:group_id>/invite/respond', GroupMembershipInviteResponseView.as_view(), name='group-respond'), # 그룹원 응답
    
    # 알림
    path("notifications", NotificationListView.as_view(), name="notification-list"),

    # access token 재발급
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),

]