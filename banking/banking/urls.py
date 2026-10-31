from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.static import serve
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT Authentication Endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='auth_login'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='auth_refresh'),

    # Application API Endpoints
    path('api/', include('accounts.urls')),
    path('api/', include('statements.urls')),
    path('api/', include('transactions.urls')),
    path('api/', include('analytics.urls')),
    path('api/', include('assistant.urls')),
    path('api/', include('reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Frontend SPA and Assets
if (settings.FRONTEND_DIST_DIR / 'index.html').exists():
    urlpatterns += [
        re_path(r'^assets/(?P<path>.*)$', serve, {'document_root': settings.FRONTEND_DIST_DIR / 'assets'}),
        path('', TemplateView.as_view(template_name='index.html'), name='frontend-root'),
        re_path(r'^(?!api/|admin/|media/|static/|assets/).*$', TemplateView.as_view(template_name='index.html'), name='frontend-spa'),
    ]
