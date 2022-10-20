from django.urls import include, path
# from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter
from .views import UsersViewSet, SubscribeViewSet

# from djoser.views import TokenCreateView, TokenDestroyView

app_name = 'users'

v2_users_router = DefaultRouter()
v2_users_router.register('users', UsersViewSet, basename='users')

# auth = [
#     path('token/login/', TokenCreateView.as_view(),
#          name='login'),
#     path('token/logout/', TokenDestroyView.as_view(),
#          name='logout'),
# ]

urlpatterns = [
    path('', include(v2_users_router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    # path('auth/', include(auth)),
    path('users/<users_id>/subscribe/',
         SubscribeViewSet.as_view({'post': 'create',
                                   'delete': 'delete'}), name='subscribe'),
]
