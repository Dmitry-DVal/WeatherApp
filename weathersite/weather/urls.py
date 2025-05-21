from django.urls import path

from . import views

urlpatterns = [
    path("", views.WeatherHomeView.as_view(), name="index"),
    path("weather/", views.ShowLocationView.as_view(), name="search"),
    path("location/add/", views.AddLocationView.as_view(), name="add_location"),
    path(
        "location/delete/<int:pk>/",
        views.DeleteWeatherCardView.as_view(),
        name="delete_location",
    ),
]
