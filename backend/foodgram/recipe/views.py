from rest_framework import viewsets

from recipe.models import (Recipe, Tag, Ingredient)
# from users.models import User
from recipe.serializers import (TagSerializer, IngredientSerializer)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    # permission_classes = any
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    # permission_classes = any
    pagination_class = None
    serializer_class = IngredientSerializer
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    # permission_classes
    # filter_class
    # filter_backends

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
