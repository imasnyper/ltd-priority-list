import datetime
from calendar import HTMLCalendar
from operator import attrgetter, methodcaller

from django.db.models import Q

from vacation.models import Vacation


class VacationCalendar(HTMLCalendar):
    def __init__(self, events=None):
        super().__init__()
        self.events = events

    def formatday(self, theyear, themonth, day, weekday, events):
        if day == 0:
            return '<td class="noday">&nbsp;</td>'

        date = datetime.date(theyear, themonth, day)

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
                if event.event_length_days() <= 1 \
                        or event.event_length_days() > 5:
                    events_html += f'<a class="calendar-event multi-day-start" href="{event.get_absolute_url()}">{event.user.username.title()}</a></br>'
                else:
                    events_html += f'<a class="calendar-event multi-day-start" href="{event.get_absolute_url()}"></a><br>'
            elif event.start_date < date < event.end_date:
                middle = event.event_length_days() // 2
                if day == middle:
                    events_html += f'<a class="calendar-event multi-day-middle" href="{event.get_absolute_url()}">{event.user.username.title()}</a></br>'
                else:
                    events_html += f'<a class="calendar-event multi-day-middle" href="{event.get_absolute_url()}"></a><br>'
            elif event.end_date.day == day:
                if event.event_length_days() <= 1 \
                        or event.event_length_days() > 5:
                    events_html += f'<a class="calendar-event multi-day-end" "href="{event.get_absolute_url()}">{event.user.username.title()}</a></br>'
                else:
                    events_html += f'<a class="calendar-event multi-day-end" href="{event.get_absolute_url()}"></a></br>'
            events_html += "</li>"
        events_html += "</ul>"

        return f"<td valign='top' class='{self.cssclasses[weekday]}'>{day}{events_html}</td>"

    def formatweek(self, theyear, themonth, theweek, events):
        s = ''.join(self.formatday(theyear, themonth, d, wd, events) for (d, wd) in theweek)
        return f"<tr>{s}</tr>"

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
