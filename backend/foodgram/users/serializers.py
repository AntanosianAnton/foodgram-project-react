from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
# from django.contrib.auth.hashers import make_password

from users.models import User
from recipe.models import Subscribe, Recipe


class UserSignupSerializer(UserCreateSerializer):
    """Сериалайзер для регистрации пользователя"""

    class Meta:
        model = User
        fields = ('email', 'username', 'id',
                  'first_name', 'last_name', 'password',)
        # extra_kwargs = {'password': {'write_only': True}}


class FollowSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'id',
                  'first_name', 'last_name',
                  'is_subscribed',)

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=user, author=obj.id).exists()


class RecipeRepresentSerializer(serializers.ModelSerializer):
    """Сериалайзер для представления модели рецепта в подписках"""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')