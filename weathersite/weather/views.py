import logging

from django.shortcuts import render
# Create your views here.

logger = logging.getLogger("weather")

def index(request):
    logger.debug("Запрос главной страницы %s", request.path)
    return render(request, "weather/index.html")


def search_weather(request):
    logger.debug("Запрос погоды %s", request.path)
    return render(request, "weather/locations.html")


def page_not_found(request, exception):
    logger.debug("Запрос не существующей страницы %s", request.path)
    return render(request, "weather/not_found.html")
