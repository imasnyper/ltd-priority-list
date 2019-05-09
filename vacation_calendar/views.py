from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView

from vacation_calendar.forms import VacationForm
from vacation_calendar.models import Vacation


# Create your views here.
class CalendarView(ListView):
    model = Vacation
    template_name = 'vacation_calendar/index.html'

    def get_queryset(selfs):
        return Vacation.objects.order_by('start_date', 'user')


class VacationAdd(CreateView):
    model = Vacation
    form_class = VacationForm
    success_url = reverse_lazy('vacation:calendar')


class VacationEdit(UpdateView):
    model = Vacation
    form_class = VacationForm
    template_name_suffix = "_update_form"
    success_url = reverse_lazy('vacation:calendar')


class VacationDelete(DeleteView):
    model = Vacation
    success_url = reverse_lazy('vacation:calendar')
