import datetime
from calendar import HTMLCalendar, monthrange
from operator import attrgetter, methodcaller

from django.db.models import Q
from django.urls import reverse

from vacation.models import Vacation


class VacationCalendar(HTMLCalendar):
    def __init__(self, events=None):
        super().__init__()
        self.events = events

    def formatday(self, theyear, themonth, day, weekday, events):
        if day == 0:
            return '<td class="noday">&nbsp;</td>'

        date = datetime.date(theyear, themonth, day)
        today = datetime.date.today()
        last_day_of_month = monthrange(theyear, themonth)[1]

        events_from_day = events.filter(Q(start_date__lte=date) & Q(end_date__gte=date))
        events_from_day = sorted(events_from_day, key=methodcaller('event_length_days'), reverse=True)
        events_from_day = sorted(events_from_day, key=attrgetter("start_date"))
        events_html = "<ul>"
        for i, event in enumerate(events_from_day):
            # TODO
            # event is a single day event
            events_html += "<li>"
            if event.is_single_day_event():
                events_html += f'<a class="calendar-event single-day-event" href="{event.get_absolute_url()}">{event.user.username.title()}</a></br>'
            # event is a multi-day event and the start date is the same as the current day being rendered
            elif event.start_date.day == day:
                if event.event_length_days() == 2 \
                        or event.event_length_days() > 5 or day == 1 or day == last_day_of_month:
                    events_html += f'<a class="calendar-event multi-day-start" href="{event.get_absolute_url()}">{event.user.username.title()}</a></br>'
                else:
                    events_html += f'<a class="calendar-event multi-day-start" href="{event.get_absolute_url()}"></a><br>'
            elif event.start_date < date < event.end_date:
                middle = event.event_length_days() // 2
                middle_day = (event.start_date + datetime.timedelta(days=middle)).day
                if day == middle_day or day == 1 or day == last_day_of_month:
                    events_html += f'<a class="calendar-event multi-day-middle" href="{event.get_absolute_url()}">{event.user.username.title()}</a></br>'
                else:
                    events_html += f'<a class="calendar-event multi-day-middle" href="{event.get_absolute_url()}"></a><br>'
            elif event.end_date.day == day:
                if event.event_length_days() == 2 \
                        or event.event_length_days() > 5 or day == last_day_of_month or day == 1:
                    events_html += f'<a class="calendar-event multi-day-end" href="{event.get_absolute_url()}">{event.user.username.title()}</a></br>'
                else:
                    events_html += f'<a class="calendar-event multi-day-end" href="{event.get_absolute_url()}"></a></br>'
            events_html += "</li>"
        events_html += "</ul>"

        if date == today:
            return f"<td valign='top' class='{self.cssclasses[weekday]}'><a href='{reverse('vacation:add', kwargs={'year': date.year, 'month': date.month, 'day': date.day})}' class='today'>{day}</a>{events_html}</td>"
        else:
            return f"<td valign='top' class='{self.cssclasses[weekday]}'><a href='{reverse('vacation:add', kwargs={'year': date.year, 'month': date.month, 'day': date.day})}'>{day}</a>{events_html}</td>"


    def formatweek(self, theyear, themonth, theweek, events):
        s = ''.join(self.formatday(theyear, themonth, d, wd, events) for (d, wd) in theweek)
        return f"<tr>{s}</tr>"

    def formatweekheader(self):
        """
        Return a header for a week as a table row.
        """
        s = ''.join(self.formatweekday(i) for i in self.iterweekdays())
        return '<tr class="week-header">%s</tr>' % s

    def formatmonth(self, theyear, themonth, withyear=True):
        events = Vacation.objects.filter(Q(start_date__month=themonth) | Q(end_date__month=themonth))



        table = []
        a = table.append
        a("<table border='0' cellpadding='0' cellspacing='0' class='month'>")
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(theyear, themonth, week, events))
            a('\n')
        # a("<\table>")
        a("\n")
        return ''.join(table)
