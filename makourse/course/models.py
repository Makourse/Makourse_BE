from django.db import models
from account.models import *

class MyPlace(models.Model): # 나만의 장소
    place_name = models.CharField(max_length=10)
    address = models.CharField(max_length=150)
    latitude = models.FloatField(default=0.0)  # 위도
    longitude = models.FloatField(default=0.0)  # 경도
    # 일단 위도, 경도를 사용할거 같아서 주소 string 필드는 안적음

    user = models.ForeignKey(User, on_delete=models.CASCADE) # 유저가 삭제되면 나만의 장소도 삭제

    def __str__(self):
        return self.place_name


class Schedule(models.Model): # 일정(코스)
    group = models.OneToOneField(UserGroup, on_delete=models.CASCADE, related_name='schedule')  # 일대일 관계 설정
    meet_date_first = models.DateField(null=True) # 만나는 날짜(최대 3개로 설정하게 하려면 조금 복잡해서 일단 이렇게 해놓음..)
    meet_date_second = models.DateField(null=True)
    meet_date_third = models.DateField(null=True)
    course_name = models.CharField(max_length=20, null=True)
    meet_place = models.CharField(max_length=50, null=True)
    latitude = models.FloatField(default=0.0)  # 만나는 장소의 위도
    longitude = models.FloatField(default=0.0)  # 만나는 장소의 경도

    def __str__(self):
        return self.course_name


class ScheduleEntry(models.Model):  # 각 코스의 일정들
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)  # 코스의 외래키
    num = models.IntegerField(null=True)  # 순번
    entry_name = models.CharField(max_length=30)  # 일정의 이름
    time = models.TimeField()  # 그 일정의 시간
    open_time = models.TimeField(null=True)  # 오픈 시간
    close_time = models.TimeField(null=True)  # 마감 시간
    category = models.CharField(max_length=10, null=True)  # 카테고리
    content = models.TextField(null=True)  # 메모
    address = models.CharField(max_length=150)
    latitude = models.FloatField(default=0.0)  # 위도
    longitude = models.FloatField(default=0.0)  # 경도

    # 순번 자동 증가 로직
    def save(self, *args, **kwargs):
        if self.num is None:  # num이 None인 경우에만 자동으로 계산
            last_entry = ScheduleEntry.objects.filter(schedule=self.schedule).order_by('-num').first()
            if last_entry:
                self.num = last_entry.num + 1  # 이전 num 값에서 +1
            else:
                self.num = 0  # 해당 schedule의 첫 번째 항목일 경우 0으로 설정
        super().save(*args, **kwargs)  # 부모 클래스의 save 호출

    def __str__(self):
        return self.entry_name




class AlternativePlace(models.Model): # 대안장소
    schedule_entry = models.ForeignKey(ScheduleEntry, on_delete=models.CASCADE)
    address = models.CharField(max_length=150)
    latitude = models.FloatField(default=0.0)  # 위도
    longitude = models.FloatField(default=0.0)  # 경도
    name = models.CharField(max_length=10) # 대안장소 이름
    category =  models.CharField(max_length=10, null=True)

    def __str__(self):
        return self.name
