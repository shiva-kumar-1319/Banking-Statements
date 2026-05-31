from django.contrib import admin
from django.urls import path,include
from django.views.generic.base import RedirectView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [

    path('',
         RedirectView.as_view(url='/api/', permanent=False)),

    path('admin/', admin.site.urls),

    path('api/token/',
         TokenObtainPairView.as_view()),

    path('api/token/refresh/',
         TokenRefreshView.as_view()),

    path('api/',
         include('accounts.urls')),

]
