from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models
from users.models import User

INGREDIENT_MIN_VALUE = 1
MIN_TIME_VALUE = 1


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Ингредиент',
        max_length=255,
        db_index=True,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=200,
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique ingredient'),
        )
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Тэг',
        max_length=200,
    )
    color = ColorField(
        format='hex',
        verbose_name='Цвет',
        help_text='Выберите цвет тега'
    )
    slug = models.SlugField(
        verbose_name='Адрес',
        unique=True,
        max_length=200,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe',
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    pub_date = models.DateField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipe/',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipe'
    )
    cooking_time = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(
            MIN_TIME_VALUE,
            'Время приготовления не может быть равно 0')],
        verbose_name='Время приготовления в минутах',
    )
    description = models.TextField(null=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_carts',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_carts',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Корзина'
        constraints = [
            models.UniqueConstraint(fields=('user', 'recipe'),
                                    name='shopping_cart')
        ]
        ordering = ('-id',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.recipe.name}, {self.user.username}'


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
        help_text='пользователь, который подпишется'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
        help_text='пользователь, на которого подписываются'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=('user', 'following'),
                                    name='subscribe')
        ]

    def __str__(self):
        return f'{self.user.username}, {self.following.username}'


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='amount',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(INGREDIENT_MIN_VALUE),)
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(fields=('ingredient', 'recipe'),
                                    name='ingredient amount')
        ]

    def __str__(self):
        return f'{self.ingredient}, {self.recipe}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites_user',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(fields=('user', 'recipe'),
                                    name='unique_favorite')
        ]

    def __str__(self):
        return f'{self.recipe.name} {self.user.username}'
