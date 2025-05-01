import logging

import requests
from django.core.cache import cache

from weathersite.settings import OW_API_KEY as api_key
from .exceptions import WeatherAPITimeoutError, WeatherAPIConnectionError, \
    WeatherAPIError, WeatherAPIInvalidRequestError, WeatherAPINoLocationsError

logger = logging.getLogger("weather")


class WeatherApiClient:
    """
    Клиент для работы с API погоды.
    """

    def __init__(self, api_key: str, use_cache=False):
        self.api_key = api_key
        self.BASE_URL = 'https://api.openweathermap.org/'
        self.use_cache = use_cache

    def search_locations_by_name(self, location_name: str, limit: int = 6,
                                 lang: str = 'rus') -> list[dict]:
        cache_key = f"geo_{location_name}"

        if self.use_cache and (cached := cache.get(cache_key)):
            return cached

        try:
            response = requests.get(
                f"{self.BASE_URL}geo/1.0/direct",
                params={
                    'q': location_name,
                    'limit': limit,
                    'appid': self.api_key,
                    'lang': lang
                },
                timeout=5
            )
            response.raise_for_status()

            locations = response.json()
            if not locations:  # API вернул пустой список
                raise WeatherAPINoLocationsError("No locations found")

            if self.use_cache:
                cache.set(cache_key, locations, 60 * 60)

            return locations
        except WeatherAPINoLocationsError as e:
            logger.error(e)
            raise WeatherAPINoLocationsError("No locations found")
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout: {str(e)}")
            raise WeatherAPITimeoutError("Service timeout") from e

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {str(e)}")
            raise WeatherAPIConnectionError("Network problem") from e

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise WeatherAPIInvalidRequestError(
                f"API error: {e.response.status_code}") from e

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)

            raise WeatherAPIError("Internal service error") from e

    def get_current_weather(self, lat: float, lon: float):
        cache_key = f"weather_{lat}_{lon}"
        logger.debug("Cache key: %s", cache_key)
        if self.use_cache:
            if cached := cache.get(cache_key):
                return cached
        try:
            response = requests.get(
                f"{self.BASE_URL}data/2.5/weather",
                params={
                    'lat': lat,
                    'lon': lon,
                    'appid': self.api_key,
                    'units': 'metric',
                    'lang': 'ru'
                },
                timeout=5
            )
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return None

        response.raise_for_status()
        data = response.json()

        # data['flag_url'] = self.get_country_flag(data['sys']['country'])
        data['icon_url'] = get_weather_icon_url(data['weather'][0]['icon'])

        if self.use_cache:
            cache.set(cache_key, data, 15 * 60)  # Кеш на 15 минут
        logger.debug("Полученные данные по коорданатам %s", data)
        return data


def get_country_flag():
    pass


def get_weather_icon_url(icon_code: str) -> str:
    """Генерация URL иконки погоды"""
    return f"https://openweathermap.org/img/wn/{icon_code}@2x.png"


if __name__ == '__main__':
    lat = 55.750446
    lon = 37.617494
    q = 'Омск'
    weather_client = WeatherApiClient(api_key)
    weather_client.get_current_weather(lat, lon)
    weather_client.search_locations_by_name(q)

# 1. Представление передает мне имя локаций, которые нужно найти.
# 2. По имени ищем доступные локации
# 3. Найденные локации выводятся на страницу
# 4. При добавлении к себе, сохранаяем координаты локаций, имя локации(Возможно в имени нет смысла).
# 5. На главном экране мы выводим все локации пользователя. (Эти локации должны быть с обновленной погодой)
# Картинка https://openweathermap.org/img/wn/04d@2x.png  # 04d == weather["icon"]
