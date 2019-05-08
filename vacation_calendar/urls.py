from django.contrib.auth.decorators import login_required
from django.urls import path

from vacation_calendar import views

app_name = 'vacation'

urlpatterns = [
    path('', login_required(views.CalendarView.as_view()), name='calendar'),
]
