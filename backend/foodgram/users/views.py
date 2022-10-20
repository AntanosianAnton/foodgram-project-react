# from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
# from django.http import HttpResponse
from djoser.views import UserViewSet

from .models import User
from recipe.models import Subscribe
from .serializers import FollowSerializer, UserSignupSerializer


class UsersViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    permission_classes = (AllowAny, )


class SubscribeViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(
        detail=True,
        methods=['post'],
        permission_classes=(IsAuthenticated, )
    )
    def subscribe(self, request, id):
        """Подписка на автора."""
        user = get_object_or_404(User, username=request.user.username)
        author = get_object_or_404(User, id=id)
        subscribtion = Subscribe.objects.filter(user=user, following=author)
        if self.request.method == 'POST':
            if user.id == author.id:
                error = {'error': 'Нельзя подписаться на себя'}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            try:
                Subscribe.objects.create(user=user, author=author)
            except IntegrityError:
                error = {'error': 'Вы уже подписаны на данного автора'}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            serializer = FollowSerializer(
                subscribtion,
                context={'request': request},
                many=True,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)