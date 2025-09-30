from django.core.management import BaseCommand
from django.db.models import Count

from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Удаление дублирующих ингредиентов из базы данных"

    def handle(self, *args, **options):
        self.stdout.write("Поиск дублирующих ингредиентов...")

        duplicates = (
            Ingredient.objects
            .values('name', 'measurement_unit')
            .annotate(count=Count('id'))
            .filter(count__gt=1)
        )

        total_removed = 0

        for duplicate in duplicates:
            ingredients = Ingredient.objects.filter(
                name=duplicate['name'],
                measurement_unit=duplicate['measurement_unit']
            ).order_by('id')

            ingredients_to_remove = ingredients[1:]
            count_to_remove = len(ingredients_to_remove)

            if count_to_remove > 0:
                self.stdout.write(
                    f"Удаляем {count_to_remove} дубликатов для "
                    f"'{duplicate['name']} ({duplicate['measurement_unit']})'"
                )

                for ingredient in ingredients_to_remove:
                    ingredient.delete()

                total_removed += count_to_remove

        self.stdout.write(
            self.style.SUCCESS(
                f"Всего удалено дублирующих ингредиентов: {total_removed}"
            )
        )

        unique_count = Ingredient.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Осталось уникальных ингредиентов: {unique_count}"
            )
        )
