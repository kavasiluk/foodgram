from rest_framework import serializers
from recipes.models import Recipe, Ingredient, Tag, Amount
from drf_extra_fields.fields import Base64ImageField

from users.serializers import UserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "slug",
        )


# 'color' - есть в задании, но нет у постмана. Нужно ли?


class AmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source="ingredient"
    )
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = Amount
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    ingredients = AmountSerializer(many=True, source="amounts")
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "name",
            "image",
            "text",
            "ingredients",
            "tags",
            "cooking_time",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def get_is_favorited(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return obj.favorited_by.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return obj.in_shopping_cart.filter(user=user).exists()
        return False

    def create(self, validated_data):
        ingredients_data = validated_data.pop("amounts")
        tags_data = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        self.create_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("amounts")
        tags_data = validated_data.pop("tags")
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags_data:
            instance.tags.set(tags_data)
        if ingredients_data:
            instance.amounts.all().delete()
            self.create_ingredients(instance, ingredients_data)
        return instance

    def create_ingredients(self, recipe, ingredients_data):
        amounts = []
        for ingredient_data in ingredients_data:
            ingredient = ingredient_data["ingredient"]
            amount = ingredient_data["amount"]
            amounts.append(
                Amount(recipe=recipe, ingredient=ingredient, amount=amount)
            )
        Amount.objects.bulk_create(amounts)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["tags"] = TagSerializer(
            instance.tags.all(), many=True
        ).data
        representation["ingredients"] = AmountSerializer(
            instance.amounts.all(), many=True
        ).data
        return representation

    def validate(self, data):
        ingredients = data.get("amounts")
        tags = data.get("tags")
        image = data.get("image")
        if not ingredients:
            raise serializers.ValidationError(
                {"ingredients": "Необходимо добавить хотя бы один ингредиент."}
            )
        if not tags:
            raise serializers.ValidationError(
                {"tags": "Необходимо выбрать хотя бы один тег."}
            )
        ingredient_ids = [
            ingredient["ingredient"].id for ingredient in ingredients
        ]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                {"ingredients": "Ингредиенты должны быть уникальными."}
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                {"tags": "Теги не должны повторяться."}
            )
        if not image:
            raise serializers.ValidationError(
                {"image": "Это поле обязательно."}
            )
        return data
