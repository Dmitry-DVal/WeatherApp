import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View, ListView

from weathersite.settings import OW_API_KEY
from .models import Location
from .services import WeatherApiClient
from .utils import WeatherSearchMixin

# Create your views here.

logger = logging.getLogger("weather")


class WeatherHomeView(LoginRequiredMixin, ListView):
    model = Location
    template_name = 'weather/index.html'
    context_object_name = 'locations_with_weather'
    # paginate_by = 4

    def get_queryset(self):
        locations = Location.objects.filter(user=self.request.user)
        return self._add_weather_data(locations)

    def _add_weather_data(self, locations):
        client = WeatherApiClient(api_key=OW_API_KEY, use_cache=True)
        return [
            client.get_current_weather(lat=loc.latitude, lon=loc.longitude)
            for loc in locations
        ]


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


class AddLocationView(LoginRequiredMixin, View):
    def post(self, request):
        Location.objects.get_or_create(
            user=request.user,
            name=request.POST.get('name'),
            latitude=request.POST.get('latitude'),
            longitude=request.POST.get('longitude'),
        )
        return redirect("index")


def page_not_found(request, exception):
    logger.debug("Запрос не существующей страницы %s", request.path)
    return render(request, "weather/not_found.html")
