from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from djoser.views import UserViewSet as DjoserUserViewSet

from users.models import CustomUser
from users.serializers import (
    UserSerializer,
    SubscriptionSerializer,
    SubscriptionCreateSerializer,
    AvatarSerializer,
)
from foodgram.pagination import CustomPagination


class UserViewSet(DjoserUserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination
    lookup_field = "id"

    def get_permissions(self):
        if self.action == "me":
            return (IsAuthenticated(),)
        return super().get_permissions()

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        author = self.get_object()
        user = request.user
        data = {"user": user.id, "author": author.id}
        serializer = SubscriptionCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        output_serializer = SubscriptionSerializer(
            author, context={"request": request}
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        author = self.get_object()
        user = request.user
        subscription = user.subscriptions.filter(author=author)
        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"errors": "Вы не подписаны на этого автора"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscriptions(self, request):
        user = request.user
        authors = [
            subscription.author
            for subscription in user.subscriptions.select_related("author")
        ]
        paginator = CustomPagination()
        page = paginator.paginate_queryset(authors, request)
        serializer = SubscriptionSerializer(
            page, many=True, context={"request": request}
        )
        return paginator.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=["put"],
        permission_classes=[IsAuthenticated],
        url_path="me/avatar",
    )
    def avatar(self, request):
        user = request.user
        serializer = AvatarSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        user = request.user
        user.avatar.delete()
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
