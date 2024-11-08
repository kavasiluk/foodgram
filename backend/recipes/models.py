from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.contrib.auth import get_user_model

from .constants import (
    MAX_LENGTH_INGREDIENT_NAME,
    MAX_LENGTH_MEASUREMENT_UNIT,
    MAX_LENGTH_TAG_NAME,
    MAX_LENGTH_COLOR_CODE,
    MAX_LENGTH_SLUG,
    MAX_LENGTH_RECIPE_NAME,
    HEX_COLOR_CODE_REGEX,
    MIN_COOKING_TIME,
    MAX_COOKING_TIME,
    MIN_INGREDIENT_AMOUNT,
    MAX_INGREDIENT_AMOUNT,
)

User = get_user_model()



class Ingredient(models.Model):
    name = models.CharField(
        verbose_name="Название ингредиента",
        max_length=MAX_LENGTH_INGREDIENT_NAME,
        db_index=True
    )
    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=MAX_LENGTH_MEASUREMENT_UNIT
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        unique_together = ("name", "measurement_unit")

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"

class Tag(models.Model):
    name = models.CharField(
        verbose_name="Название тега",
        max_length=MAX_LENGTH_TAG_NAME,
        unique=True
    )
    color = models.CharField(
        verbose_name="Цвет",
        max_length=MAX_LENGTH_COLOR_CODE,
        unique=True,
        validators=[
            RegexValidator(
                regex=HEX_COLOR_CODE_REGEX,
                message="Введите корректный HEX-код цвета"
            )
        ],
    )
    slug = models.SlugField(
        verbose_name="Уникальный слаг",
        max_length=MAX_LENGTH_SLUG,
        unique=True
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name

class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    name = models.CharField(
        max_length=MAX_LENGTH_RECIPE_NAME,
        verbose_name="Название"
    )
    image = models.ImageField(
        upload_to="recipes/",
        verbose_name="Изображение"
    )
    text = models.TextField(verbose_name="Описание")
    ingredients = models.ManyToManyField(
        Ingredient,
        through="Amount",
        related_name="recipes",
        verbose_name="Ингредиенты",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        verbose_name="Теги"
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN_COOKING_TIME),
            MaxValueValidator(MAX_COOKING_TIME)
        ],
        verbose_name="Время приготовления (в минутах)",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации"
    )

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name

class Amount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="amounts",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="amounts",
        verbose_name="Ингредиент",
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN_INGREDIENT_AMOUNT),
            MaxValueValidator(MAX_INGREDIENT_AMOUNT)
        ],
        verbose_name="Количество"
    )

    class Meta:
        unique_together = ("recipe", "ingredient")
        verbose_name = "Количество ингредиента"
        verbose_name_plural = "Количество ингредиентов"

    def __str__(self):
        return f"{self.ingredient.name} - {self.amount}"

class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name="Рецепт",
    )

    class Meta:
        unique_together = ("user", "recipe")
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные рецепты"

    def __str__(self):
        return f"{self.user.username} -> {self.recipe.name}"

class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="in_shopping_cart",
        verbose_name="Рецепт",
    )

    class Meta:
        unique_together = ("user", "recipe")
        verbose_name = "Корзина покупок"
        verbose_name_plural = "Корзины покупок"

    def __str__(self):
        return f"{self.user.username} -> {self.recipe.name}"
