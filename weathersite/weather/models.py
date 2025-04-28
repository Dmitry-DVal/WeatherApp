from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Location(models.Model):
    name = models.CharField(max_length=100)
    users = models.ForeignKey(User, on_delete=models.CASCADE)
    Latitude = models.DecimalField(max_digits=10, decimal_places=7)
    Longitude = models.DecimalField(max_digits=10, decimal_places=7)
