from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipe.models import Recipe
from users.models import User


class UserSignupSerializer(UserCreateSerializer):
    """Сериалайзер для регистрации пользователя"""

    class Meta:
        model = User
        fields = ('email', 'username', 'id',
                  'first_name', 'last_name', 'password',)


class RecipeSubsSerializer(serializers.ModelSerializer):
    """Сериалайзер для представления модели рецепта в подписках"""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(
        read_only=True,
        method_name='get_is_subscribed')

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (
            not user.is_anonymous
            and obj.following.filter(user=user).exists()
        )


class FollowSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        read_only=True,
        method_name='get_is_subscribed')
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes'
    )
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed', 'recipes',
                  'recipes_count',)

    # def get_is_subscribed(self, obj):
    #     user = self.context.get('request').user
    #     if user.is_anonymous:
    #         return False
    #     return Subscribe.objects.filter(user=user, following=obj.id).exists()
    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (
            not user.is_anonymous
            and obj.following.filter(user=user).exists()
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit_recipes = request.query_params.get('recipes_limit')
        if limit_recipes is not None:
            queryset = obj.recipe.all()[:(int(limit_recipes))]
        else:
            queryset = obj.recipe.all()
        context = {'request': request}
        return RecipeSubsSerializer(queryset, many=True,
                                    context=context).data

    @staticmethod
    def get_recipes_count(obj):
        return obj.recipe.count()
