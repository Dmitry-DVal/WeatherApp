from django.shortcuts import render


# Create your views here.

def index(request):
    return render(request, "weather/index.html")


def search_weather(request):
    return render(request, "weather/locations.html")


def page_not_found(request, exception):
    return render(request, "weather/not_found.html")
