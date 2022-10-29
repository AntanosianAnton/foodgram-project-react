import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipe.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                           ShoppingCart, Tag)
from users.models import User
from users.serializers import UserSignupSerializer

INGREDIENT_MIN_VALUE = 1
MIN_TIME_VALUE = 1


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
    """ Сериалайзер для добавления ингредиентов """
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


class PurchaseListSerializer(serializers.ModelSerializer):
    """
    Сериалайзер добавленя рецепта в список покупок
    """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'coocking_time')


class RecipeReprpesentSerializer(serializers.ModelSerializer):
    """Сериалайзер для отображения сведений о рецепте"""
    id = serializers.PrimaryKeyRelatedField(source='ingredient.id',
                                            read_only=True)
    name = serializers.SlugRelatedField(slug_field='name',
                                        source='ingredient.name',
                                        read_only=True)
    measurement_unit = serializers.SlugRelatedField(
        slug_field='measurment_unit',
        source='ingredient',
        read_only=True)

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериалайзер для избранного"""
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Favorite
        fields = '__all__'

    def validate(self, data):
        user = data['user']
        recipe_id = data['recipe'].id
        favorite_exists = Favorite.objects.filter(
            user=user,
            recipe_id=recipe_id
            ).exists()
        if favorite_exists:
            raise ValidationError(
                'Рецепт уже добавлен в избранное!'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReprpesentSerializer(instance.recipe,
                                          context=context).data


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class CheckRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для проверки рецепта"""
    tags = TagSerializer(many=True, read_only=True)
    author = UserSignupSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    @staticmethod
    def get_ingredients(obj):
        ingredients = IngredientAmount.objects.filter(recipe=obj)
        return RecipeReprpesentSerializer(ingredients, many=True).data

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Favorite.objects.filter(recipe=obj, user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj).exists()


class RecipeSerializer(serializers.ModelSerializer):
    """ Сериалайзер для рецептов """
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    ingredients = AddIngredientSerializer(many=True)
    author = UserSignupSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'image', 'text',
                  'ingredients', 'tags', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart',)

    def get_ingredients(self, obj):
        queryset = IngredientAmount.objects.filter(recipe=obj)
        return RecipeReprpesentSerializer(queryset, many=True)

    def validate_ingredients(self, ingredients):
        ingredients_list = []
        for ingredient in ingredients:
            if len(ingredients_list) <= INGREDIENT_MIN_VALUE:
                raise ValidationError('Добавьте ингридиент')
            if not Ingredient.objects.filter(
                    id=ingredients['ingredient']['id']).exists():
                raise ValidationError('Такого ингредиента нет')
            if Ingredient.objects.filter(
                    id=ingredients['ingredient']['id']) in ingredients_list:
                raise ValidationError(f'{ingredient} уже есть в рецепте!')
            ingredients_list.append(Ingredient.objects.filter(
                id=ingredients['ingredient']['id']))
        return ingredients

    @staticmethod
    def validate_time(value):
        if value <= MIN_TIME_VALUE:
            raise ValidationError('Время приготовления не может быть равно 0')
        return value

    @staticmethod
    def create_tags_ingredients(tags, ingredients, recipe):
        for tag in tags:
            recipe.tags.add(tag)
        for ingredient in ingredients:
            IngredientAmount.objects.create(
                recipe=recipe, ingredient=ingredient['id'],
                amount=ingredient['amount']
            )

    def create(self, validated_data):
        author = self.context.get('request').user
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        image = validated_data.pop('image')
        recipe = Recipe.objects.create(image=image, author=author,
                                       **validated_data)
        self.create_tags_ingredients(tags_data, ingredients_data, recipe)
        return recipe

    def update(self, recipe, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        IngredientAmount.objects.filter(recipe=recipe).delete()
        self.create_tags_ingredients(tags_data, ingredients_data, recipe)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return PurchaseListSerializer(instance, context=context).data


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return PurchaseListSerializer(instance.recipe, context=context).data
