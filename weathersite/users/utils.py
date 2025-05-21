from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect


class RedirectAuthenticatedUserMixin:
    redirect_url = "index"

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect(self.redirect_url)
        return super().dispatch(request, *args, **kwargs)  # type: ignore
