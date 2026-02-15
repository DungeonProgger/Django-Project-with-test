from django.test import TestCase
from django.urls import reverse


class TestRoutes(TestCase):
    def test_cheese_list_route(self):
        response = self.client.get(reverse("cheese_list"))
        self.assertEqual(response.status_code, 200)

    # def test_cheese_detail_route(self):
        # response = self.client.get(reverse("cheese_detail", args=[1]))
        # self.assertEqual(response.status_code, 200)

    def test_about_route(self):
        response = self.client.get(reverse("about"))
        self.assertEqual(response.status_code, 200)
