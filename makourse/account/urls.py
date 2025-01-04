from django.urls import path
from .views import JoinGroupView,UserGroupView, GroupMembershipView, GroupScheduleView

urlpatterns = [

    # 그룹 만들기
    path('schedules/<int:schedule_id>/group', UserGroupView.as_view(), name='schedule-group'),

    path('groups/join', JoinGroupView.as_view(), name='join-group'), # 그룹원 등록
    path('groups/<int:group_id>/members', GroupMembershipView.as_view(), name='group-members'), # 그룹의 그룹원 보기
    path('groups/<int:group_id>/members/<int:membership_id>', GroupMembershipView.as_view(), name='group-member-delete'), # 그룹원 삭제
    path('groups/<int:group_id>/schedules', GroupScheduleView.as_view(), name='group-schedules'),


]