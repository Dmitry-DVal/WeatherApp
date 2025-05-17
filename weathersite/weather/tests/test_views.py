from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from weather.models import Location
from unittest.mock import patch

class WeatherViewsHomePageTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser',
                                                         password='pass123')
        self.client.login(username='testuser', password='pass123')
        self.url = reverse('index')

    def test_homepage_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weather/index.html')

    def test_homepage_context_with_no_locations(self):
        response = self.client.get(self.url)
        self.assertContains(response, "You don&#x27;t have any saved locations yet.")

    def test_homepage_with_user_location(self):
        Location.objects.create(user=self.user, name='Москва', latitude=55.75,
                                longitude=37.61)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('locations_with_weather', response.context)

    def test_homepage_returns_302(self):
        self.client.logout()
        response = self.client.get(self.url)
        redirect_url = reverse('users:login') + '?next=' + self.url
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)


class ShowLocationViewTestCase(TestCase):
    """Тесты страницы поиска локаций (ShowLocationView)."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='pass123')
        self.client.login(username='testuser', password='pass123')
        self.url = reverse('search')


    def test_search_location_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weather/locations.html')
        self.assertContains(response, "Please enter a city name")

    def test_search_location_returns_302(self):
        self.client.logout()
        response = self.client.get(self.url)
        redirect_url = reverse('users:login') + '?next=' + self.url
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    @patch('weather.views.ShowLocationView.handle_search')
    def test_search_view_valid_city_query(self, mock_handle_search):
        """Проверка успешного поиска по городу."""
        mock_handle_search.return_value = (
            [{'name': 'Москва', 'lat': 55.75, 'lon': 37.61}],
            None  # error
        )
        response = self.client.get(self.url + '?city=Москва')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weather/locations.html')
        self.assertIn('locations', response.context)
        self.assertIn('query', response.context)
        self.assertNotIn('error', response.context)

    @patch('weather.views.ShowLocationView.handle_search')
    def test_search_view_error_from_api(self, mock_handle_search):
        """Проверка случая с ошибкой API."""
        mock_handle_search.return_value = (None, "Ошибка соединения")
        response = self.client.get(self.url + '?city=Москва')
        self.assertContains(response, "Ошибка соединения")
        self.assertTemplateUsed(response, 'weather/locations.html')