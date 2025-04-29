from django.urls import path

from . import views

urlpatterns = [
    path("", views.WeatherHomeView.as_view(), name="index"),
    path("weather/", views.search_weather),
]
