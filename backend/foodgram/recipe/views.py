from rest_framework import viewsets, status
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework.permissions import (AllowAny,
                                        IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)
from rest_framework.response import Response
from rest_framework.decorators import action

from recipe.models import (Recipe, Tag, Ingredient, Favorite,
                           ShoppingCart)
from recipe.serializers import (CheckRecipeSerializer, RecipeSerializer,
                                ShoppingCartSerializer,
                                TagSerializer, IngredientSerializer,
                                FavoriteSerializer,)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = None
    serializer_class = IngredientSerializer
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    # filter_class =
    filter_backends = (DjangoFilterBackend,)
    # pagination_class =

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
