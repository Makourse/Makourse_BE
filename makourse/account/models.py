from django.db import models
from django.utils.crypto import get_random_string # 초대링크 생성
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission

def generate_unique_code():
    return get_random_string(length=30)

# 사용자 생성 및 슈퍼유저 생성 관리
class CustomUserManager(BaseUserManager):
    def create_user(self, user_id, password=None, **extra_fields): # ID와 비밀번호로 일반 사용자 생성 및 저장
        if not user_id:
            raise ValueError('ID는 필수 항목입니다.')
        user = self.model(user_id=user_id, **extra_fields)  # user 객체 생성
        user.set_password(password)  # 비밀번호 설정
        user.save(using=self._db)  # 데이터베이스에 저장
        return user

    # 주어진 ID와 비밀번호로 슈퍼유저 생성 및 저장
    def create_superuser(self, user_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(user_id, password, **extra_fields)

# 커스텀 유저 모델 - ID로 로그인
class CustomUser(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(max_length=30, unique=True)  # 사용자 ID 필드
    is_staff = models.BooleanField(default=False)  # 관리자 사이트 접근 가능 여부
    is_superuser = models.BooleanField(default=False)  # 슈퍼유저 여부
    is_active = models.BooleanField(default=True)  # 활성화 상태 여부
    date_joined = models.DateTimeField(auto_now_add=True)  # 계정 생성 날짜

    objects = CustomUserManager()  # 커스텀 유저 매니저 지정

    USERNAME_FIELD = 'user_id'  # 로그인에 사용할 사용자 ID 필드
    REQUIRED_FIELDS = []  # 슈퍼유저 생성 시 추가로 요구할 필드 없음

    # 그룹과 권한 필드에 대해 충돌 방지를 위해 related_name 설정
    #이거없이도 원래 충돌 안나고 마이그레이션 됐는데 자꾸 빨간 오류들 떠서 추가함,, 이유는 아직 머르곘어 찾아볼겡
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_groups',  # 충돌 방지를 위해 related_name 설정
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',  # 설명
        verbose_name='groups'  # 관리자 사이트에서의 필드 이름
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions',  # 충돌 방지를 위해 related_name 설정
        blank=True,
        help_text='Specific permissions for this user.',  # 설명
        verbose_name='user permissions'  # 관리자 사이트에서의 필드 이름
    )

    def __str__(self):
        return self.user_id

# 사용자
class User(models.Model):
    id = models.CharField(max_length=100, unique=True, primary_key=True) # id
    password = models.CharField(max_length=100) # pwd
    name = models.CharField(max_length=30) # 이름
    profile_image = models.ImageField(upload_to='user_photo/', null=True, blank=True) # 프로필 사진
    field = models.BooleanField(default=False) # 이용약관 동의 여부

    def __str__(self): 
        return self.id


class UserGroup(models.Model):
    code = models.CharField(
        max_length=30,
        unique=True,
        default=generate_unique_code  # 전역 함수로 대체
    )

    def generate_code(self):  # 초대링크 생성 함수
        self.code = get_random_string(length=30)
        self.save()

    def __str__(self):
        # code가 None인 경우 기본 문자열 반환
        return self.code if self.code else "Unnamed UserGroup"



class GroupMembership(models.Model):
    ROLE_CHOICES = [
        ('leader', '모임장'),
        ('member', '모임원'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(UserGroup, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')  # 역할 필드 추가

    class Meta:
        unique_together = ('user', 'group')  # 동일한 사용자가 같은 그룹에 중복 가입하지 않도록

    def __str__(self):
        schedule_name = self.group.schedule.course_name if hasattr(self.group, 'schedule') and self.group.schedule else "No Schedule"
        return f"{schedule_name}의 {self.user.name}({self.get_role_display()})"

# user와 group은 다대다 관계인듯
# 한 user가 여러 그룹에 들어갈 수 있고, 한 group 안에도 여러 유저가 있을 수 있으니까
# 그래서 GroupMembership으로 이어주는걸로 짬