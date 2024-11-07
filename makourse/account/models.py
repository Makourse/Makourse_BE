from django.db import models
from django.utils.crypto import get_random_string # 초대링크 생성

# 사용자
class User(models.Model):
    id = models.CharField(max_length=100, unique=True, primary_key=True) # id
    password = models.CharField(max_length=100) # pwd
    name = models.CharField(max_length=30) # 이름
    profile_image = models.ImageField(upload_to='user_photo/') # 프로필 사진
    field = models.BooleanField(default=False) # 이용약관 동의 여부

    def __str__(self): 
        return self.id

class UserGroup(models.Model):
    code = models.CharField(max_length=30, unique=True, default=get_random_string)
    
    def generate_code(self): # 초대링크 생성 함수
        self.code = get_random_string(length=30)
        self.save()

    def __str__(self):
        self.code

class GroupMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(UserGroup, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'group')  # 동일한 사용자가 같은 그룹에 중복 가입하지 않도록

    def __str__(self):
        return f"{self.user.name} in group {self.group.code}"

# user와 group은 다대다 관계인듯
# 한 user가 여러 그룹에 들어갈 수 있고, 한 group 안에도 여러 유저가 있을 수 있으니까
# 그래서 GroupMembership으로 이어주는걸로 짬