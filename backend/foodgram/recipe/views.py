import datetime

from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from foodgram.pagination import CustomPagination
from recipe.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                           ShoppingCart, Tag)
from recipe.serializers import (CheckRecipeSerializer, IngredientSerializer,
                                PurchaseListSerializer, RecipeSerializer,
                                TagSerializer)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .filters import IngredientSearchFilter, RecipeFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    pagination_class = None
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    default_serializer_class = RecipeSerializer
    filter_class = RecipeFilter
    filter_backends = (DjangoFilterBackend,)
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return CheckRecipeSerializer
        return RecipeSerializer

    @action(detail=True,
            permission_classes=(IsAuthenticated,),
            methods=['POST', 'DELETE'], )
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            ShoppingCart.objects.get_or_create(
                user=user,
                recipe=recipe,
            )
            serializer = PurchaseListSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        purchase_list = get_object_or_404(
            ShoppingCart,
            user=user,
            recipe=recipe
        )
        purchase_list.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            Favorite.objects.get_or_create(
                user=user,
                recipe=recipe,
            )
            serializer = PurchaseListSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        favorite = get_object_or_404(
            Favorite,
            user=user,
            recipe=recipe
        )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        purchase_list = {}
        ingredients = IngredientAmount.objects.filter(
            recipe__recipe_carts__user=request.user
        )
        for ingredient in ingredients:
            name = ingredient.ingredient.name
            amount = ingredient.amount
            measurement_unit = ingredient.ingredient.measurement_unit
            if name not in purchase_list:
                purchase_list[name] = {
                    'measurement_unit': measurement_unit,
                    'amount': amount
                }
            else:
                purchase_list[name]['amount'] += amount
        main_list = ([f"* {item}:{value['amount']}"
                      f"{value['measurement_unit']}\n"
                      for item, value in purchase_list.items()])
        today = datetime.date.today()
        main_list.append(f'\n Enjoy your meal with Foodgram, {today.year}')
        response = HttpResponse(main_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="BuyList.txt"'
        return response
