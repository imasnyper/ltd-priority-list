import calendar
import datetime

from django.urls import reverse_lazy, reverse
from django.utils import timezone as tz
from django.utils.safestring import mark_safe
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView

from vacation.calendar import VacationCalendar
from vacation.forms import VacationForm
from vacation.models import Vacation


# Create your views here.
class CalendarView(ListView):
    model = Vacation
    template_name = 'vacation/index.html'

    def get_queryset(self, *args, **kwargs):
        return Vacation.objects.order_by('start_date', 'user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)

        cal = VacationCalendar()
        cal.setfirstweekday(calendar.SUNDAY)

        if 'year' in self.kwargs.keys():
            now = tz.datetime(self.kwargs['year'], self.kwargs['month'], 1)
            html_calendar = cal.formatmonth(self.kwargs['year'], self.kwargs['month'], withyear=True)
        else:
            now = tz.now()
            html_calendar = cal.formatmonth(now.year, now.month, withyear=True)

        prev_month = tz.datetime(now.year, now.month, 1)
        prev_month = prev_month - datetime.timedelta(days=1)
        prev_month = tz.datetime(prev_month.year, prev_month.month, 1)

        last_day = calendar.monthrange(now.year, now.month)[1]
        next_month = tz.datetime(now.year, now.month, last_day)
        next_month = next_month + datetime.timedelta(days=1)
        next_month = tz.datetime(next_month.year, next_month.month, 1)

        context['prev_month'] = reverse('vacation:calendar',
                                        kwargs={'year': prev_month.year, 'month': prev_month.month})
        context['next_month'] = reverse('vacation:calendar',
                                        kwargs={'year': next_month.year, 'month': next_month.month})

        html_calendar = html_calendar.replace('<td ', '<td height="150"')
        context['calendar'] = mark_safe(html_calendar)
        return context


class VacationDetail(DetailView):
    model = Vacation


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
