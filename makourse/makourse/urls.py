from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg       import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Makourse",
        default_version='1.0',
        description="Makourse-project API 문서",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="admin@admin.com"), # 부가정보
        license=openapi.License(name="backend"),     # 부가정보
    ),
    public=True,
    permission_classes=(AllowAny,),
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('course/', include('course.urls')),
    path('account/',include('account.urls')),

     # Swagger url
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


