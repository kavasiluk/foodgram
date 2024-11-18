from django.http import HttpResponse
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from recipes.models import (
    Recipe,
    Ingredient,
    Tag,
    Favorite,
    ShoppingCart,
    Amount,
)
from recipes.serializers import (
    RecipeSerializer,
    IngredientSerializer,
    TagSerializer,
)
from recipes.short_serializers import RecipeShortSerializer
from recipes.permissions import IsAuthorOrReadOnly
from recipes.filters import IngredientFilter, RecipeFilter
from foodgram.pagination import CustomPagination


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = (
        Recipe.objects.all()
        .select_related("author")
        .prefetch_related("tags", "ingredients")
    )
    serializer_class = RecipeSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    permission_classes = [IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        if user.favorites.filter(recipe=recipe).exists():
            return Response(
                {"errors": "Рецепт уже в избранном"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Favorite.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(
            recipe, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        favorite = user.favorites.filter(recipe=recipe)
        if favorite.exists():
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"errors": "Рецепт отсутствует в избранном"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        if user.shopping_cart.filter(recipe=recipe).exists():
            return Response(
                {"errors": "Рецепт уже в корзине покупок"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ShoppingCart.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(
            recipe, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        cart_item = user.shopping_cart.filter(recipe=recipe)
        if cart_item.exists():
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"errors": "Рецепт отсутствует в корзине покупок"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart_items = ShoppingCart.objects.filter(
            user=user
        ).values_list("recipe", flat=True)
        if not shopping_cart_items.exists():
            return Response(
                {"error": "Ваша корзина покупок пуста."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ingredients = (
            Amount.objects.filter(recipe__in=shopping_cart_items)
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(total_amount=Sum("amount"))
        )

        shopping_list = ""
        for ingredient in ingredients:
            name = ingredient["ingredient__name"]
            measurement_unit = ingredient["ingredient__measurement_unit"]
            amount = ingredient["total_amount"]
            shopping_list += f"{name} ({measurement_unit}) - {amount}\n"

        response = HttpResponse(shopping_list, content_type="text/plain")
        response["Content-Disposition"] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    def custom_exception_handler(exc, context):
        response = exception_handler(exc, context)
        return response

    @action(detail=True, methods=["get"], url_path="get-link")
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        short_link = self.generate_short_link(recipe)
        return Response({"short-link": short_link}, status=status.HTTP_200_OK)

    def generate_short_link(self, recipe):
        return f"https://short.link/{recipe.id}"


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    filter_backends = (IngredientFilter,)
    search_fields = ["^name"]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [permissions.AllowAny]
