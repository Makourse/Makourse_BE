from django.urls import path
from .views import UserGroupView, GroupMembershipView
urlpatterns = [

    # 그룹 보기
    path('schedules/<int:schedule_id>/group', UserGroupView.as_view(), name='schedule-group'),

    path('groups/<int:group_id>/join', GroupMembershipView.as_view(), name='group-join'), # 그룹원 등록
    path('groups/<int:group_id>/members/<int:membership_id>', GroupMembershipView.as_view(), name='group-member-delete'), # 그룹원 삭제


]