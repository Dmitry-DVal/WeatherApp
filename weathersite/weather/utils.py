import logging
from typing import Any

from django.db.models import QuerySet

from weather.exceptions import (
    WeatherAPINoLocationsError,
    WeatherAPITimeoutError,
    WeatherAPIConnectionError,
    WeatherAPIError,
)
from weather.models import Location
from weather.services import WeatherApiClient
from weathersite.settings import OW_API_KEY

logger = logging.getLogger("weather")


class WeatherSearchMixin:
    def get_weather_client(self) -> WeatherApiClient:
        return WeatherApiClient(api_key=OW_API_KEY, use_cache=True)

    def handle_search(
        self, query: str
    ) -> tuple[list[dict[str, Any]] | None, str | None]:
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
    def get_weather_client(self) -> WeatherApiClient:
        return WeatherApiClient(api_key=OW_API_KEY, use_cache=True)

    def handle_weather_request(
        self, locations: QuerySet[Location]
    ) -> tuple[list[dict[str, Any]], str | None]:
        client = self.get_weather_client()
        results = []
        error = None

        try:
            for loc in locations:
                weather_data = client.get_current_weather(
                    lat=float(loc.latitude), lon=float(loc.longitude)
                )

                results.append({**weather_data, "name": loc.name, "db_id": loc.pk})
                logger.debug(results)
        except WeatherAPITimeoutError:
            error = "Service timeout. Please try again later."
            logger.error("Weather API failed: %s", error)
        except WeatherAPIConnectionError:
            error = "Network problem. Check your internet connection."
            logger.error("Weather API failed: %s", error)
        except WeatherAPIError:
            error = "Weather service temporary unavailable"
            logger.error("Weather API failed: %s", error)

        return results, error
