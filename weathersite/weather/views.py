import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView

from weather.services import WeatherApiClient
from weathersite.settings import OW_API_KEY
from .exceptions import WeatherAPITimeoutError, WeatherAPIConnectionError, \
    WeatherAPIError, WeatherAPIInvalidRequestError, WeatherAPINoLocationsError

# Create your views here.

logger = logging.getLogger("weather")


class WeatherHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'weather/index.html'


class ShowLocationView(LoginRequiredMixin, TemplateView):
    template_name = "weather/locations.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('city', '').strip()

        if not query:
            context['info'] = "Please enter a city name"
            return context

        try:
            client = WeatherApiClient(api_key=OW_API_KEY, use_cache=True)
            context['locations'] = client.search_locations_by_name(query)
            context['query'] = query

        except WeatherAPINoLocationsError as e:
            context['info'] = "No locations found"
            context['query'] = query
        except WeatherAPIInvalidRequestError as e:
            context['error'] = str(e)
        except (WeatherAPITimeoutError, WeatherAPIConnectionError) as e:
            context['error'] = str(e)
        except WeatherAPIError as e:
            context['error'] = "Service temporary unavailable"
            logger.error(f"Weather API failure: {str(e)}")

        return context


def page_not_found(request, exception):
    logger.debug("Запрос не существующей страницы %s", request.path)
    return render(request, "weather/not_found.html")
