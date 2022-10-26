from django.urls import include, path
# from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from recipe.views import TagViewSet, IngredientViewSet, RecipeViewSet

app_name = 'recipe'

v1_recipe_router = DefaultRouter()
v1_recipe_router.register('tags', TagViewSet, basename='tags')
v1_recipe_router.register('ingredients',
                          IngredientViewSet, basename='ingredients')
v1_recipe_router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(v1_recipe_router.urls)),
]
