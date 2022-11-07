from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from .models import Recipe, Tag


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(FilterSet):
    """
    Фильтры для сортировки рецептов по:
    тегам, нахождению в избранном и корзине.
    """
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',)
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart',
        label='shopping_cart',)

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'favorites', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, view, value):
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, view, value):
        # if value:
        #     return queryset.filter(recipe_carts__user=self.request.user)
        # return queryset
        return Recipe.objects.filter(
            recipe_carts__user=self.request.user) if value else None
