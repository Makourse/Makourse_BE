from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission

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
class User(AbstractBaseUser, PermissionsMixin):
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
