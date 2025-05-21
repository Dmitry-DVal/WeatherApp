import logging
from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View, ListView, DeleteView

from .models import Location
from .utils import WeatherSearchMixin, WeatherDataMixin

# Create your views here.

logger = logging.getLogger("weather")


class WeatherHomeView(LoginRequiredMixin, WeatherDataMixin, ListView):
    model = Location
    template_name = "weather/index.html"
    context_object_name = "locations_with_weather"
    paginate_by = 8

    def get_queryset(self) -> QuerySet[Location]:
        locations = Location.objects.filter(user=self.request.user)
        return self._add_weather_data(locations)  # type: ignore

    def _add_weather_data(self, locations: QuerySet[Location]) -> list[dict[str, Any]]:
        weather_data, error = self.handle_weather_request(locations)
        if error:
            self.error = error
        return weather_data

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if hasattr(self, "error"):
            context["error"] = self.error
        elif not context["locations_with_weather"]:
            context["info"] = "You don't have any saved locations yet."
        return context


class ShowLocationView(LoginRequiredMixin, WeatherSearchMixin, TemplateView):
    template_name = "weather/locations.html"
    extra_context = {"title": "Search."}

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("city", "").strip()
        logger.debug("Query: %s", query)

        if not query:
            logger.warning("No city specified")
            context["info"] = "Please enter a city name"
            return context

        locations, error = self.handle_search(query)
        if error:
            context["error"] = error
        else:
            context.update({"locations": locations, "query": query})
        return context


class DeleteWeatherCardView(DeleteView):
    model = Location
    success_url = reverse_lazy("index")

    def get_queryset(self) -> QuerySet[Location]:
        logger.warning("User %s deleted location", self.request.user)
        return super().get_queryset().filter(user=self.request.user)


class AddLocationView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest) -> HttpResponse:
        Location.objects.get_or_create(
            user=request.user,
            name=request.POST.get("name"),
            latitude=request.POST.get("latitude"),
            longitude=request.POST.get("longitude"),
        )
        logger.info(
            "User %s added location: %s", request.user, request.POST.get("name")
        )

        return redirect("index")


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    logger.warning("404 Not Found: %s", request.path)
    return render(request, "weather/not_found.html")
