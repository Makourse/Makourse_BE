from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
import json, os
from decouple import config
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

secret_file = BASE_DIR / 'secrets.json'

with open(secret_file) as file:
    secrets = json.loads(file.read())

def get_secret(setting,secrets_dict = secrets):
    try:
        return secrets_dict[setting]
    except KeyError:
        error_msg = f'Set the {setting} environment variable'
        raise ImproperlyConfigured(error_msg)

SECRET_KEY = get_secret('SECRET_KEY') 

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    # my apps
    'account',
    'course',
    # basic apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #external apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_yasg',
    'rest_framework_simplejwt.token_blacklist', # 로그아웃 구현
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS=[
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',

]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_ORIGINS = True

ROOT_URLCONF = 'makourse.urls'

AUTH_USER_MODEL = 'account.CustomUser'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny', # 개발용
        #'rest_framework.permissions.IsAuthenticated',  # 인증된 요청인지 확인
       ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # JWT를 통한 인증방식 사용
    ),
}

REST_USE_JWT = True

SIMPLE_JWT = {
    'SIGNING_KEY': 'hellomakourse',
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

SOCIAL_REDIRECT_URIS = {
    'google': 'http://localhost:8000/account/google/callback/',
    'naver': 'http://localhost:8000/account/naver/callback/',
    'kakao': 'http://localhost:8000/account/kakao/callback/',
}


SOCIAL_KEYS = {
    'google': { # 이후 프론트랑 합치면 자바스크립트 원본에 프론트 주소 추가하기
        'client_id': config('GOOGLE_CLIENT_ID'),
        'client_secret': config('GOOGLE_CLIENT_SECRET'),
    },
    'naver': {
        'client_id': config('NAVER_CLIENT_ID'),
        'client_secret': config('NAVER_CLIENT_SECRET'),
    },
    'kakao': {
        'client_id': config('KAKAO_CLIENT_ID'),
        'client_secret': config('KAKAO_CLIENT_SECRET'),
    }
}


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'makourse.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'ko'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
#https://docs.djangoproject.com/en/5.1/howto/static-files/

# 정적 파일 URL 경로
STATIC_URL = '/static/'

# 운영 환경에서 정적 파일이 수집되는 디렉토리
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# 개발 환경에서 사용하는 정적 파일 디렉토리들
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  # 프로젝트 내 'static' 폴더
]
MEDIA_URL = '/media/'  # 미디어 파일 URL 경로
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # 미디어 파일 저장 경로
# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
