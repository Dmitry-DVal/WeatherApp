from django.urls import path

from . import views

urlpatterns = [
    path("", views.index),
    path("weather/", views.search_weather),
]



