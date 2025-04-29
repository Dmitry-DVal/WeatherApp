import logging
from msilib.schema import ListView

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

logger = logging.getLogger("weather")

class WeatherHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'weather/index.html'



@login_required
def search_weather(request):
    logger.debug("Запрос погоды %s", request.path)
    return render(request, "weather/locations.html")


def page_not_found(request, exception):
    logger.debug("Запрос не существующей страницы %s", request.path)
    return render(request, "weather/not_found.html")
