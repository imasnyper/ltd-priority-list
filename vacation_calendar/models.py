from django.contrib.auth.models import User
from django.db import models


# create your models here.
class Vacation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
