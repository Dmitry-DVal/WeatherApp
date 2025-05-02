import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView

from .utils import WeatherSearchMixin

# Create your views here.

logger = logging.getLogger("weather")


class WeatherHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'weather/index.html'


class ShowLocationView(LoginRequiredMixin, WeatherSearchMixin, TemplateView):
    template_name = "weather/locations.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('city', '').strip()
        logger.debug("Query: %s", query)

        if not query:
            logger.warning("No city specified")
            context['info'] = "Please enter a city name"
            return context

        locations, error = self.handle_search(query)
        if error:
            context['error'] = error
        else:
            context.update({
                'locations': locations,
                'query': query
            })
        return context


def page_not_found(request, exception):
    logger.debug("Запрос не существующей страницы %s", request.path)
    return render(request, "weather/not_found.html")
