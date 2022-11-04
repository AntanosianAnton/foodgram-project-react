from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from .models import Recipe


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(FilterSet):
    """
    Фильтры для сортировки рецептов по:
    тегам, нахождению в избранном и корзине.
    """
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorite = filters.BooleanFilter(method='filter_is_favorite')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorite', 'is_in_shopping_cart')

    def filter_is_favorite(self, queryset, value):
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, value):
        if value:
            return queryset.filter(carts__user=self.request.user)
        return queryset
