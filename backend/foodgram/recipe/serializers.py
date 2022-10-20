import base64
from rest_framework import serializers

from django.core.files.base import ContentFile

from recipe.models import (Recipe, Tag, Ingredient,)

# from users.models import User


class TagSerializer(serializers.ModelSerializer):
    """ Сериалайзер  для тега """
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """ Сериалайзер для ингредиентов """
    class Meta:
        model = Ingredient
        fields = '__all__'


class AddIngredientSerializer(serializers.ModelSerializer):
    """ Сериалайзер для обавлеения ингредиентов """
    amount = serializers.IntegerField()
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    """ Сериалайзер для рецептов """
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = AddIngredientSerializer(many=True)
    # author = serializer for user
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'image', 'text',
                  'ingredients', 'tags', 'cooking_time',
                  'is_favorited')
