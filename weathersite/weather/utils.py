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


class WeatherDataMixin:
    def get_weather_client(self):
        return WeatherApiClient(api_key=OW_API_KEY, use_cache=True)

    def handle_weather_request(self, locations):
        client = self.get_weather_client()
        results = []
        error = None

        try:
            for loc in locations:
                weather_data = client.get_current_weather(
                    lat=loc.latitude,
                    lon=loc.longitude
                )
                results.append(weather_data)
        except WeatherAPITimeoutError:
            error = "Service timeout. Please try again later."
        except WeatherAPIConnectionError:
            error = "Network problem. Check your internet connection."
        except WeatherAPIError:
            error = "Weather service temporary unavailable"

        return results, error