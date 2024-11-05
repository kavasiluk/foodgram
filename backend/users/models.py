from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(verbose_name="Email адрес", unique=True)

    avatar = models.ImageField(
        upload_to="avatars/", verbose_name="Аватар", blank=True, null=True
    )

    first_name = models.CharField("first name", max_length=150, blank=False)

    last_name = models.CharField("last name", max_length=150, blank=False)

    REQUIRED_FIELDS = ["username", "first_name", "last_name"]
    USERNAME_FIELD = "email"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="subscribers",
        verbose_name="Автор",
    )

    class Meta:
        unique_together = ("user", "author")
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f"{self.user} подписан на {self.author}"
