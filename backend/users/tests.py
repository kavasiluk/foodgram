from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from users.models import CustomUser, Subscription


class UserAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            email="user@example.com", password="testpassword"
        )
        self.author = CustomUser.objects.create_user(
            email="author@example.com", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)

    def test_subscribe(self):
        response = self.client.post(f"/api/users/{self.author.id}/subscribe/")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Subscription.objects.filter(
                user=self.user, author=self.author
            ).exists()
        )

    def test_unsubscribe(self):
        Subscription.objects.create(user=self.user, author=self.author)
        response = self.client.delete(
            f"/api/users/{self.author.id}/subscribe/"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Subscription.objects.filter(
                user=self.user, author=self.author
            ).exists()
        )

    def test_subscriptions_list(self):
        Subscription.objects.create(user=self.user, author=self.author)
        response = self.client.get("/api/users/subscriptions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
