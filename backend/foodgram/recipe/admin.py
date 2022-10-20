from django.contrib import admin

from recipe.models import (Ingredient, Tag, Recipe,
                           ShoppingCart, Subscribe, IngredientAmount,
                           Favorite)


class IngredientAmountInline(admin.TabularInline):
    model = IngredientAmount
    extra = 0


@admin.register(Ingredient)
class AdminIngredient(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', )
    empty_value_display = '-пусто-'
    list_filter = ('name',)


@admin.register(Tag)
class AdminTag(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name',)
    empty_value_display = '-пусто-'
    list_filter = ('name',)


@admin.register(ShoppingCart)
class AdminCart(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'id')
    search_fields = ('user',)
    empty_value_display = '-пусто-'
    list_display = ('user',)


@admin.register(Favorite)
class AdminFavorite(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user',)
    empty_value_display = '-пусто- '
    list_display = ('user',)


@admin.register(Recipe)
class AdminRecipe(admin.ModelAdmin):
    inlines = (IngredientAmountInline,)
    list_display = ('name', 'author', 'cooking_time',
                    'id', 'count_favorite', 'pub_date')
    search_fields = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'
    list_filter = ('name', 'author', 'tags')

    def count_favorite(self, obj):
        return Favorite.objects.filter(recipe=obj).count()
    count_favorite.short_description = 'Число добавлении в избранное'


@admin.register(Subscribe)
class AdminSubscribe(admin.ModelAdmin):
    list_display = ('user', 'following')
    search_fields = ('user', )
    empty_value_display = '-пусто-'
    list_filter = ('user',)
