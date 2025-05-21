from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from weather.models import Location


class WeatherViewsHomePageTestCase(TestCase):
    """Home page tests."""

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(  # type: ignore
            username="testuser",
            password="pass123",
        )
        self.client.login(username="testuser", password="pass123")
        self.url = reverse("index")

    def test_homepage_returns_200(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "weather/index.html")

    def test_homepage_context_with_no_locations(self) -> None:
        response = self.client.get(self.url)
        self.assertContains(response, "You don&#x27;t have any saved locations yet.")

    def test_homepage_with_user_location(self) -> None:
        Location.objects.create(
            user=self.user, name="Москва", latitude=55.75, longitude=37.61
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("locations_with_weather", response.context)

    def test_homepage_returns_302(self) -> None:
        self.client.logout()
        response = self.client.get(self.url)
        redirect_url = reverse("users:login") + "?next=" + self.url
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_paginate_homepage(self) -> None:
        for i in range(12):
            Location.objects.create(
                user=self.user, name=f"Город{i}", latitude=55.0 + i, longitude=37.0 + i
            )

        response_page_1 = self.client.get(self.url + "?page=1")
        response_page_2 = self.client.get(self.url + "?page=2")

        self.assertEqual(response_page_1.status_code, 200)
        self.assertEqual(response_page_2.status_code, 200)

        self.assertEqual(len(response_page_1.context["locations_with_weather"]), 8)
        self.assertEqual(len(response_page_2.context["locations_with_weather"]), 4)

    def test_custom_404_handler(self) -> None:
        response = self.client.get("/some/nonexistent/page/")
        self.assertTemplateUsed(response, "weather/not_found.html")


class ShowLocationViewTestCase(TestCase):
    """Tests of the location search page (ShowLocationView)."""

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(  # type: ignore
            username="testuser",
            password="pass123",
        )
        self.client.login(username="testuser", password="pass123")
        self.url = reverse("search")

    def test_search_location_returns_200(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "weather/locations.html")
        self.assertContains(response, "Please enter a city name")

    def test_search_location_returns_302(self) -> None:
        self.client.logout()
        response = self.client.get(self.url)
        redirect_url = reverse("users:login") + "?next=" + self.url
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    @patch("weather.views.ShowLocationView.handle_search")
    def test_search_view_valid_city_query(self, mock_handle_search: MagicMock) -> None:
        mock_handle_search.return_value = (
            [{"name": "Москва", "lat": 55.75, "lon": 37.61}],
            None,  # error
        )
        response = self.client.get(self.url + "?city=Москва")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "weather/locations.html")
        self.assertIn("locations", response.context)
        self.assertIn("query", response.context)
        self.assertNotIn("error", response.context)

    @patch("weather.views.ShowLocationView.handle_search")
    def test_search_view_error_from_api(self, mock_handle_search: MagicMock) -> None:
        mock_handle_search.return_value = (None, "Ошибка соединения")
        response = self.client.get(self.url + "?city=Москва")
        self.assertContains(response, "Ошибка соединения")
        self.assertTemplateUsed(response, "weather/locations.html")


class AddLocationViewTestCase(TestCase):
    """Tests adding a location (AddLocationView)."""

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(  # type: ignore
            username="testuser",
            password="pass123",
        )
        self.client.login(username="testuser", password="pass123")
        self.url = reverse("add_location")  # проверь, правильно ли назван путь

    def test_add_location_post_creates_location(self) -> None:
        data = {"name": "Москва", "latitude": 55.75, "longitude": 37.61}

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("index"))

        location = Location.objects.get(user=self.user, name="Москва")
        self.assertEqual(float(location.latitude), 55.75)
        self.assertEqual(float(location.longitude), 37.61)

    def test_add_location_unauthenticated_redirect(self) -> None:
        self.client.logout()
        data = {"name": "Тест", "latitude": 10.0, "longitude": 20.0}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("users:login")))  # type: ignore


class DeleteLocationViewTestCase(TestCase):
    """DeleteLocationView (DeleteLocationView) Tests."""

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(  # type: ignore
            username="testuser", password="pass123"
        )
        self.client.login(username="testuser", password="pass123")

        self.location = Location.objects.create(
            user=self.user, name="Москва", latitude=55.75, longitude=37.61
        )
        self.url = reverse("delete_location", args=[self.location.pk])

    def test_delete_own_location(self) -> None:
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("index"))
        self.assertFalse(Location.objects.filter(pk=self.location.pk).exists())

    def test_cannot_delete_other_users_location(self) -> None:
        other_user = get_user_model().objects.create_user(  # type: ignore
            username="otheruser",
            password="123",
        )
        foreign_location = Location.objects.create(
            user=other_user, name="Воронеж", latitude=51.66, longitude=39.20
        )
        url = reverse("delete_location", args=[foreign_location.pk])

        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Location.objects.filter(pk=foreign_location.pk).exists())
