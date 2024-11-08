from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from recipes.models import Ingredient, Tag, Recipe
from recipes.constants import RECIPE_COOKING_TIME, RECIPE_INGREDIENT_AMOUNT
from users.models import CustomUser


class RecipeAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            email="test@example.com", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)

    def test_create_recipe(self):
        ingredient = Ingredient.objects.create(
            name="Sugar", measurement_unit="g"
        )
        tag = Tag.objects.create(
            name="Dessert", color="#FF0000", slug="dessert"
        )
        data = {
            "name": "Test Recipe",
            "text": "Test description",
            "cooking_time": RECIPE_COOKING_TIME,
            "ingredients": [
                {"id": ingredient.id, "amount": RECIPE_INGREDIENT_AMOUNT}
            ],
            "tags": [tag.id],
            "image": None,
        }
        response = self.client.post(
            reverse("recipes-list"), data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Recipe.objects.count(), 1)
        self.assertEqual(Recipe.objects.get().name, "Test Recipe")
