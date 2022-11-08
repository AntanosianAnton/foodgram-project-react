from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipe.models import Subscribe

from .models import User
from .serializers import FollowSerializer


class UsersViewSet(UserViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        subscribtion = User.objects.filter(following__user=request.user)
        pages = self.paginate_queryset(subscribtion)
        serializer = FollowSerializer(
            pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        """Подписка на автора."""
        user = request.user
        follow_to = get_object_or_404(User, id=id)
        subscription = Subscribe.objects.filter(user=user, following=follow_to)
        if request.method == 'POST' and user.username != follow_to.username:
            Subscribe.objects.get_or_create(user=user, following=follow_to)
            serializer = FollowSerializer(
                follow_to, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if self.request.method == 'DELETE' and subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error':
                'Вы не подписаны на данного пользователя '
                'или подписываетесь на себя!'},
            status=status.HTTP_400_BAD_REQUEST)
