from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


# create your models here.
class Vacation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

    def is_single_day_event(self):
        return self.start_date == self.end_date

    def event_length_days(self):
        return (self.end_date - self.start_date).days + 1

    def get_absolute_url(self):
        return reverse('vacation:detail', args=[self.pk])

    def __repr__(self):
        return f"{self.user.username.title()}: {self.start_date} - {self.end_date}"

    def __str__(self):
        return f"{self.user.username.title()}: {self.start_date} - {self.end_date}"
