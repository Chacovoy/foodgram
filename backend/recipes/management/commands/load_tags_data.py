from csv import DictReader

from django.core.management import BaseCommand

from recipes.models import Tag


ALREDY_LOADED_ERROR_MESSAGE = """
If you need to reload the child data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables"""


class Command(BaseCommand):
    help = "Загрузка данных из tags.csv"

    def handle(self, *args, **options):

        print("Загрузка тагов.")

        count = 0
        skipped = 0
        for row in DictReader(open('./data/tags.csv', encoding='utf-8')):
            if not Tag.objects.filter(slug=row['slug']).exists():
                tag = Tag(
                    name=row['name'],
                    slug=row['slug'],
                    color=row['color'],
                )
                tag.save()
                count += 1
            else:
                skipped += 1

        print(f'Успешно загружено {count} тагов, '
              f'пропущено дубликатов: {skipped}')
