import logging

from weather.exceptions import WeatherAPINoLocationsError, WeatherAPITimeoutError, \
    WeatherAPIConnectionError, WeatherAPIError
from weather.services import WeatherApiClient
from weathersite.settings import OW_API_KEY

logger = logging.getLogger("weather")


class WeatherSearchMixin:
    def get_weather_client(self):
        return WeatherApiClient(api_key=OW_API_KEY, use_cache=True)

    def handle_search(self, query: str):
        try:
            client = self.get_weather_client()
            return client.search_locations_by_name(query), None
        except WeatherAPINoLocationsError:
            return None, "No locations found"
        except WeatherAPITimeoutError:
            return None, "Service timeout. Please try again later."
        except WeatherAPIConnectionError:
            return None, "Network problem. Check your internet connection."
        except WeatherAPIError:
            return None, "Weather service temporary unavailable"
