from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import UsersViewSet

app_name = 'users'

v2_users_router = DefaultRouter()
v2_users_router.register('users', UsersViewSet, basename='users')

urlpatterns = [
    path('', include(v2_users_router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
