from csv import reader

from django.core.management.base import BaseCommand
from recipe.models import Ingredient, Tag


class Command(BaseCommand):
    """
    Наполняем базу ингредиентами
    после миграции БД запускаем командой
    python manage.py load_ingredients локально
    или
    sudo docker-compose exec backend python manage.py load_ingredients
    на удаленном сервере.
    """
    def handle(self, *args, **kwargs):
        with open(
                'recipe/data/ingredients.csv', 'r',
                encoding='UTF-8'
        ) as ingredients:
            for row in reader(ingredients):
                if len(row) == 2:
                    Ingredient.objects.get_or_create(
                        name=row[0], measurement_unit=row[1],
                    )
        with open(
                'recipe/data/tags.csv', 'r',
                encoding='UTF-8'
        ) as tags:
            for row in reader(tags):
                if len(row) == 3:
                    Tag.objects.get_or_create(
                        name=row[0], color=row[1], slug=row[2])
