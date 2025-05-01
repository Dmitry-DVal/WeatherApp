from django.urls import path

from . import views

urlpatterns = [
    path("", views.WeatherHomeView.as_view(), name="index"),
    # path("weather/", views.search_weather, name="search"),
    path("weather/", views.ShowLocationView.as_view(), name="search"),
]
