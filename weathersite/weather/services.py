import logging

import requests
from django.core.cache import cache

from .exceptions import WeatherAPITimeoutError, WeatherAPIConnectionError, \
    WeatherAPIError, WeatherAPIInvalidRequestError, WeatherAPINoLocationsError

logger = logging.getLogger("weather")


class WeatherAPIExceptionHandler:
    """Обработка общих исключений."""

    @staticmethod
    def handle_exceptions(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.Timeout as e:
                logger.error(f"Timeout: {str(e)}")
                raise WeatherAPITimeoutError("Service timeout")
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Connection error: {str(e)}")
                raise WeatherAPIConnectionError("Network problem")
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
                raise WeatherAPIInvalidRequestError(
                    f"API error: {e.response.status_code}")
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}", exc_info=True)
                raise WeatherAPIError("Internal service error") from e

        return wrapper


class WeatherApiClient:
    BASE_URL = 'https://api.openweathermap.org/'
    TIMEOUT = 5
    DEFAULT_CACHE_TTL = 60 * 60  # Кэширование на 1 час.

    def __init__(self, api_key: str, use_cache=False):
        self.api_key = api_key
        self.use_cache = use_cache

    @WeatherAPIExceptionHandler.handle_exceptions
    def _make_request(self, endpoint: str, params: dict) -> dict:
        """Базовый метод для выполнения запросов"""
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.get(url, params=params, timeout=self.TIMEOUT)
        response.raise_for_status()
        return response.json()

    def _get_cached_data(self, cache_key: str):
        return cache.get(cache_key) if self.use_cache else None

    def _set_cached_data(self, cache_key: str, data, ttl: int | None = None):
        if self.use_cache:
            cache.set(cache_key, data, ttl or self.DEFAULT_CACHE_TTL)

    def search_locations_by_name(self, location_name: str, limit: int = 6,
                                 lang: str = 'rus') -> list[dict]:
        cache_key = f"geo_{location_name}_{limit}_{lang}"
        if cached := self._get_cached_data(cache_key):
            logger.debug("Returning cached locations data")
            return cached

        params = {
            'q': location_name,
            'limit': limit,
            'appid': self.api_key,
            'lang': lang
        }

        data = self._make_request('geo/1.0/direct', params)
        logger.debug(data)

        if not data:
            raise WeatherAPINoLocationsError("No locations found")

        data = self._deduplicate_locations(data)

        data = self._check_local_name(data)


        self._set_cached_data(cache_key, data)
        return data

    def get_current_weather(self, lat: float, lon: float, units: str = 'metric',
                            lang: str = 'ru') -> dict:
        cache_key = f"weather_{lat}_{lon}_{units}_{lang}"
        if cached := self._get_cached_data(cache_key):
            logger.debug("Returning cached weather data")
            return cached

        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': units,
            'lang': lang
        }

        data = self._make_request('data/2.5/weather', params)
        enriched_data = self._enrich_weather_data(data)

        self._set_cached_data(cache_key, enriched_data, 15 * 60)  # 15 минут для погоды
        return enriched_data

    def _enrich_weather_data(self, data: dict) -> dict:
        """Добавляем дополнительные вычисляемые поля"""
        if not data:
            return None

        return {
            **data,
            'icon_url': get_weather_icon_url(data['weather'][0]['icon']),
            'timezone': format_timezone(data['timezone']),
        }

    def _check_local_name(self, data, lang='ru'):
        for location in data:
            if 'local_names' in location and lang in location['local_names']:
                if location['local_names'][lang] != location['name']:
                    location['name'] = location['local_names'][lang]
        return data


    def _deduplicate_locations(self, data):
        """Удаляем дубликаты (город+страна) сохраняя первое вхождение"""
        seen = set()
        unique_locations = []

        for loc in data:
            # Ключ для проверки дублей: название + код страны
            key = (loc['name'].lower(), loc['country'])

            if key not in seen:
                seen.add(key)
                unique_locations.append(loc)

        return unique_locations

def get_weather_icon_url(icon_code: str) -> str:
    """Генерация URL иконки погоды"""
    return f"https://openweathermap.org/img/wn/{icon_code}@2x.png"


def format_timezone(seconds):
    hours = seconds // 3600
    return f"UTC+{hours}" if hours >= 0 else f"UTC{hours}"
