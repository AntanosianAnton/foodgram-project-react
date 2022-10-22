from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.http import HttpResponse
from djoser.views import UserViewSet

from .models import User
from recipe.models import Subscribe
from .serializers import FollowSerializer, UserSignupSerializer


class UsersViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    permission_classes = (AllowAny, )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated, )
    )
    def subscribe(self, request, id):
        """Подписка на автора."""
        user = get_object_or_404(User, username=request.user.username)
        author = get_object_or_404(User, id=id)
        if self.request.method == 'POST':
            if user.id == author.id:
                error = {'error': 'Вы не можете подписаться на себя'}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            try:
                Subscribe.objects.get_or_create(user=user, following=author)
            except IntegrityError:
                error = {'error': f'Вы уже подписаны на {author}'}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            serializer = FollowSerializer(
                author,
                context={'request': request},
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            try:
                subscription = Subscribe.objects.get(user=user,
                                                     following=author)
            except ObjectDoesNotExist:
                error = {'error': f'Вы не подписаны на {author}'}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            subscription.delete()
            return HttpResponse(f'Вы успешно отписаны от {author}',
                                status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated, )
    )
    def subscriptions(self, request):
        subscription = User.objects.filter(following__user=self.request.user)
        pages = self.paginate_queryset(subscription)
        if pages:
            serializer = FollowSerializer(
                pages,
                context={'request': request},
            )
            return self.get_paginated_response(serializer.data)
        serializer = FollowSerializer(
            subscription,
            many=True,
            context={'request': request},
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
