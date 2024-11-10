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


class SeheduleEntry(models.Model): # 각 코스의 일정들
    sehedule = models.ForeignKey(Schedule, on_delete=models.CASCADE) # 코스의 외래키

    num = models.IntegerField() # 순번이 차례로 증가하게 해야되는지 아니면 나중에 결정해야하는지..
    entry_name = models.CharField(max_length=10) # 일정의 이름
    time = models.TimeField() # 그 일정의 시간

    open_time = models.TimeField() # 오픈 시간
    close_time = models.TimeField() # 마감시간
    # 운영시간은 이렇게 오픈, 마감 시간으로 따로 저장

    category =  models.CharField(max_length=10, null=True)
    # 일단 char로 만들었는데 나중에 Choice로 변경해야될거 같으면 그때 하자!
    # category는 지도 api에서 가져오는 거니까 모델에 따로 필요가 없나..?

    content = models.TextField(null=True) # 메모

    address = models.CharField(max_length=150)
    latitude = models.FloatField(default=0.0)  # 위도
    longitude = models.FloatField(default=0.0)  # 경도

    # 순번 생성 (save 함수 오버로딩)
    def save(self, *args, **kwargs):
        if not self.num:
            last_num = SeheduleEntry.objects.filter(sehedule=self.sehedule).order_by('-num').first()

            if last_num:
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.num = new_num

        super().save(*args, **kwargs) #객체 저장
            

    def __str__(self):
        return self.entry_name

class AlternativePlace(models.Model): # 대안장소
    schedule_entry = models.ForeignKey(SeheduleEntry, on_delete=models.CASCADE)

    address = models.CharField(max_length=150)
    latitude = models.FloatField(default=0.0)  # 위도
    longitude = models.FloatField(default=0.0)  # 경도

    name = models.CharField(max_length=10) # 대안장소 이름

    category =  models.CharField(max_length=10, null=True)

    def __str__(self):
        return self.name
