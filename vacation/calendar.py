from calendar import HTMLCalendar

from vacation.models import Vacation


class VacationCalendar(HTMLCalendar):
    def __init__(self, events=None):
        super().__init__()
        self.events = events

    def formatday(self, day, weekday, events):
        events_start_lte = events.filter(start_date__day__lte=day)
        events_end_gte = events.filter(end_date__day__gte=day)
        events_from_day = events_end_gte.intersection(events_start_lte)
        events_from_day = events_from_day.order_by("start_date")
        events_from_day = sorted(events_from_day, key=lambda x: x.event_length_days(), reverse=True)
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
            elif event.start_date.day < day < event.end_date.day:
                middle = (event.start_date.day + event.end_date.day) // 2
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

        if day == 0:
            return '<td class="noday">&nbsp;</td>'
        else:
            return f"<td valign='top' class='{self.cssclasses[weekday]}'>{day}{events_html}</td>"

    def formatweek(self, theweek, events):
        s = ''.join(self.formatday(d, wd, events) for (d, wd) in theweek)
        return f"<tr>{s}</tr>"

    def formatmonth(self, theyear, themonth, withyear=True):
        events = Vacation.objects.filter(start_date__month__gte=themonth)

        table = []
        a = table.append
        a("<table border='0' cellpadding='0' cellspacing='0' class='month'>")
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week, events))
            a('\n')
        # a("<\table>")
        a("\n")
        return ''.join(table)
