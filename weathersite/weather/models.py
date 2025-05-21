from django.contrib.auth.models import User
from django.db import models


# Create your models here.


class Location(models.Model):
    name = models.CharField(max_length=100)  # type: ignore[var-annotated]
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # type: ignore[var-annotated]
    latitude = models.DecimalField(max_digits=10, decimal_places=7)  # type: ignore[var-annotated]
    longitude = models.DecimalField(max_digits=10, decimal_places=7)  # type: ignore[var-annotated]

    def __str__(self) -> str:
        return self.name
