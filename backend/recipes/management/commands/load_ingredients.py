import csv
from django.core.management.base import BaseCommand
from recipes.models import Ingredient
from django.conf import settings
import os


class Command(BaseCommand):
    help = "Загружает ингредиенты из CSV-файла"

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR, "data", "ingredients.csv")
        try:
            with open(file_path, encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                #                Ingredient.objects.all().delete()  # Опционально: удаляем существующие данные
                for row in reader:
                    if len(row) == 2:
                        name, measurement_unit = row
                        Ingredient.objects.create(
                            name=name, measurement_unit=measurement_unit
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f"Неверная строка: {row}")
                        )
            self.stdout.write(
                self.style.SUCCESS("Ингредиенты успешно загружены.")
            )
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Файл не найден: {file_path}"))
