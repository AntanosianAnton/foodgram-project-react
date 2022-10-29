from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from recipe.models import Recipe, Subscribe
from users.models import User

# from django.contrib.auth.hashers import make_password



class UserSignupSerializer(UserCreateSerializer):
    """Сериалайзер для регистрации пользователя"""

    class Meta:
        model = User
        fields = ('email', 'username', 'id',
                  'first_name', 'last_name', 'password',)
        # extra_kwargs = {'password': {'write_only': True}}


class RecipeRepresentSerializer(serializers.ModelSerializer):
    """Сериалайзер для представления модели рецепта в подписках"""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
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
        return Subscribe.objects.filter(user=user, following=obj.id).exists()

    def get_recipe(self, obj):
        request = self.context.get('request')
        limit_recipes = request.query_params.get('recipes_limit')
        if limit_recipes is not None:
            queryset = obj.recipes.all()[:(int(limit_recipes))]
        else:
            queryset = obj.recipes.all()
        context = {'request': request}
        return RecipeRepresentSerializer(queryset, many=True,
                                         context=context).data

    @staticmethod
    def get_recipes_count(obj):
        return obj.recipes.count()
