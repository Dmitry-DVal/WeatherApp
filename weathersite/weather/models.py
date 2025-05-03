from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Location(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)


    def __str__(self):
        return self.name


