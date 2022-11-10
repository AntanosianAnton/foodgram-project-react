from drf_extra_fields.fields import Base64ImageField
from recipe.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                           ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.models import User
from users.serializers import UserSignupSerializer

INGREDIENT_MIN_VALUE = 1
MIN_TIME_VALUE = 1


class TagSerializer(serializers.ModelSerializer):
    """ Сериалайзер  для тега """
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


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
    Сериалайзер добавления рецепта в список покупок
    """
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class RecipeReprpesentSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        read_only=True
    )
    name = serializers.SlugRelatedField(
        slug_field='name',
        source='ingredient',
        read_only=True
    )
    measurement_unit = serializers.SlugRelatedField(
        slug_field='measurement_unit',
        source='ingredient',
        read_only=True
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CheckRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для проверки рецепта"""
    tags = TagSerializer(many=True, read_only=True)
    author = UserSignupSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(
        method_name='get_ingredients')
    image = Base64ImageField()
    is_favorite = serializers.SerializerMethodField(
        method_name='get_is_favorite')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart')
    name = serializers.CharField(max_length=200)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorite', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time')

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
    cooking_time = serializers.IntegerField()
    name = serializers.CharField(max_length=200)

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'image', 'text',
                  'ingredients', 'tags', 'cooking_time',)

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise ValidationError(
                'Необходимо выбрать ингредиенты!'
            )
        for ingredient in ingredients:
            if int(ingredient['amount']) < INGREDIENT_MIN_VALUE:
                raise ValidationError(
                    'Количество ингредиентов должно быть больше нуля!'
                )
        ids = [item['id'] for item in ingredients]
        if len(ids) != len(set(ids)):
            raise ValidationError(
                'Ингредиенты в рецепте должны быть уникальными!'
            )
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
        return CheckRecipeSerializer(instance, context=context).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe_id = data['recipe'].id
        if ShoppingCart.objects.filter(user=user,
                                       recipe__id=recipe_id).exists():
            raise ValidationError(
                'Рецепт уже добавлен в корзину!'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return PurchaseListSerializer(instance.recipe, context=context).data
