import datetime

from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from foodgram.pagination import CustomPagination
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipe.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                           ShoppingCart, Tag)
from recipe.serializers import (CheckRecipeSerializer, FavoriteSerializer,
                                IngredientSerializer, RecipeSerializer,
                                ShoppingCartSerializer, TagSerializer)
from .permissions import IsAuthorOrAdmin
from .filters import IngredientSearchFilter, RecipeFilter


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdmin,)
    filter_class = (RecipeFilter,)
    filter_backends = (DjangoFilterBackend,)
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return CheckRecipeSerializer
        return RecipeSerializer

    @staticmethod
    def post_method(request, pk, serializers):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializers.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_method(request, pk, model):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        model_obj = get_object_or_404(model, user=user, recipe=recipe)
        model_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated)
    )
    def favorite(self, request, pk):
        if self.request.method == 'POST':
            return self.post_method(request=request,
                                    pk=pk,
                                    serializers=FavoriteSerializer)
        if self.request.method == 'DELETE':
            return self.delete_method(request=request,
                                      pk=pk,
                                      model=Favorite)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=(IsAuthenticated)
    )
    def shopping_cart(self, request, pk):
        if self.request.method == 'POST':
            return self.post_method(request=request,
                                    pk=pk,
                                    serializers=ShoppingCartSerializer)
        if self.request.method == 'DELETE':
            return self.delete_method(request=request,
                                      pk=pk,
                                      model=ShoppingCart)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def download_purchase_list(self, request):
        purchase_list = {}
        ingredients = IngredientAmount.objects.filter(
            recipe__purch__user=request.user).values_list(
                'ingredient__name', 'ingredient__measurement_unit',
                'quantity', 'recipe__name'
        )
        for ingredient in ingredients:
            name = ingredient.ingredient.name
            amount = ingredient.amount
            measurment_unit = ingredient.ingredient.measurment_unit
            if name not in purchase_list:
                purchase_list[name] = {
                    'measurment_unit': measurment_unit,
                    'amount': amount
                }
            else:
                purchase_list[name]['amount'] += amount
        main_list = ([f"* {item}:{value['amount']}"
                      f"{value['measurement_unit']}\n"
                      for item, value in purchase_list.items()])
        today = datetime.date.today()
        main_list.append(f'\n From FoodGram with love, {today.year}')
        response = HttpResponse(main_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="BuyList.txt"'
        return response
