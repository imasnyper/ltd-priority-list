from django.views.generic.list import ListView

from vacation_calendar.models import Vacation


# Create your views here.
class CalendarView(ListView):
    model = Vacation
    template_name = 'vacation_calendar/index.html'
