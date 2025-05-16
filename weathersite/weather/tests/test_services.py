from unittest.mock import patch, Mock

from django.core.cache import cache
from django.test import TestCase
from requests.exceptions import Timeout, HTTPError, ConnectionError

from weather.exceptions import WeatherAPINoLocationsError, WeatherAPITimeoutError, \
    WeatherAPIConnectionError, WeatherAPIInvalidRequestError
from weather.services import WeatherApiClient


class WeatherApiClientTest(TestCase):
    def setUp(self):
        self.client = WeatherApiClient(api_key="test_key", use_cache=True)
        cache.clear()

    @patch('weather.services.requests.get')
    def test_search_locations_by_name_success(self, mock_get):
        """Проверяем корректный ответ от API для поиска локаций."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            "name": "Москва",
            "local_names": {"ru": "Москва"},
            "lat": 55.7558,
            "lon": 37.6173,
            "country": "RU"
        }]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = self.client.search_locations_by_name("Москва")

        self.assertEqual(result[0]["name"], "Москва")
        self.assertEqual(result[0]["country"], "RU")

    @patch('weather.services.requests.get')
    def test_search_locations_by_name_no_results(self, mock_get):
        """Проверяем поведение при пустом списке локаций или с несуществующим городом."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        with self.assertRaises(WeatherAPINoLocationsError):
            self.client.search_locations_by_name("NonexistentСity")

        with self.assertRaises(WeatherAPINoLocationsError):
            self.client.search_locations_by_name("")

    @patch('weather.services.requests.get')
    def test_api_timeout_error(self, mock_get):
        """Имитируем Timeout от requests"""
        mock_get.side_effect = Timeout("The request timed out")

        with self.assertRaises(WeatherAPITimeoutError):
            self.client.search_locations_by_name("Москва")

        with self.assertRaises(WeatherAPITimeoutError):
            self.client.get_current_weather(55.754, 37.6204)

    @patch('weather.services.requests.get')
    def test_api_connection_error(self, mock_get):
        """Имитируем ConnectionError"""
        mock_get.side_effect = ConnectionError("Network problem")

        with self.assertRaises(WeatherAPIConnectionError):
            self.client.search_locations_by_name("Москва")
            self.client.get_current_weather(55.754, 37.6204)

    @patch('weather.services.requests.get')
    def test_api_http_error(self, mock_get):
        """Имитируем HTTPError (например, 404 или 500)"""
        mock_response = Mock()
        http_error = HTTPError(response=Mock(status_code=404, text="Not Found"))
        mock_response.raise_for_status.side_effect = http_error
        mock_get.return_value = mock_response

        with self.assertRaises(WeatherAPIInvalidRequestError):
            self.client.search_locations_by_name("Москва")
            self.client.get_current_weather(55.754, 37.6204)

    @patch('weather.services.requests.get')
    def test_get_current_weather_success(self, mock_get):
        """Проверяем корректный ответ от API для получения погоды."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'coord': {'lon': 37.6204, 'lat': 55.754},
            'weather': [{
                'id': 803,
                'main': 'Clouds',
                'description': 'облачно с прояснениями',
                'icon': '04d'
            }],
            'main': {
                'temp': 23.17,
                'feels_like': 22.4,
                'temp_min': 23.17,
                'temp_max': 23.17,
                'pressure': 1016,
                'humidity': 33,
                'sea_level': 1016,
                'grnd_level': 997
            },
            'visibility': 10000,
            'wind': {'speed': 5.67, 'deg': 192, 'gust': 7.39},
            'clouds': {'all': 66},
            'dt': 1747394977,
            'sys': {'country': 'RU', 'sunrise': 1747358173, 'sunset': 1747416945},
            'timezone': 10800,
            'id': 524901,
            'name': 'Москва',
            'cod': 200
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = self.client.get_current_weather(55.754, 37.6204)

        self.assertEqual(result['name'], 'Москва')
        self.assertIn('icon_url', result)
        self.assertEqual(result['timezone'], 'UTC+3')

    @patch('weather.services.requests.get')
    def test_get_current_weather_sets_cache(self, mock_get):
        """Проверяем, что данные сохраняются в кэш при первом вызове."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'coord': {'lon': 37.6204, 'lat': 55.754},
            'weather': [
                {'id': 803, 'main': 'Clouds', 'description': 'облачно', 'icon': '04d'}],
            'main': {'temp': 20.0, 'feels_like': 19.0, 'temp_min': 20.0,
                     'temp_max': 20.0, 'pressure': 1000, 'humidity': 60,
                     'sea_level': 1000, 'grnd_level': 990},
            'visibility': 10000,
            'wind': {'speed': 3.0, 'deg': 180},
            'clouds': {'all': 40},
            'dt': 1234567890,
            'sys': {'country': 'RU', 'sunrise': 1234567000, 'sunset': 1234600000},
            'timezone': 10800,
            'id': 123456,
            'name': 'Москва',
            'cod': 200
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = self.client.get_current_weather(55.754, 37.6204)
        cache_key = "weather_55.754_37.6204_metric_ru"

        # Проверим, что данные кэшировались
        cached = cache.get(cache_key)
        self.assertIsNotNone(cached)
        self.assertEqual(result, cached)

    @patch('weather.services.requests.get')
    def test_get_current_weather_uses_cache(self, mock_get):
        """Проверяем, что при наличии данных в кэше API не вызывается повторно."""
        cache_key = "weather_55.754_37.6204_metric_ru"
        fake_cached_data = {"cached": "weather"}

        # Заранее положили в кэш данные
        cache.set(cache_key, fake_cached_data, 15 * 60)

        result = self.client.get_current_weather(55.754, 37.6204)

        self.assertEqual(result, fake_cached_data)
        mock_get.assert_not_called()

