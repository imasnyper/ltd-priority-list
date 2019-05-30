import datetime
from calendar import HTMLCalendar, monthrange, month_name, day_abbr, weekday
from operator import attrgetter, methodcaller

from django.db.models import Q
from django.urls import reverse
from workalendar.america import Ontario

from vacation.models import Vacation


class VacationCalendar(HTMLCalendar):
    def __init__(self, events=None):
        super().__init__()
        self.events = events
        self.event_dict = {}

    def formatday(self, theyear, themonth, date, events):
        wday = weekday(date.year, date.month, date.day)
        day = date.day
        if day == 0:
            return '<td class="noday">&nbsp;</td>'

        empty_rows = 0

        today = datetime.date.today()
        last_day_of_month = monthrange(theyear, themonth)[1]
        ontario = Ontario()
        ontario_holidays = ontario.holidays(theyear)

        events_from_day = events.filter(Q(start_date__lte=date) & Q(end_date__gte=date))
        events_from_day = sorted(events_from_day, key=methodcaller('event_length_days'), reverse=True)
        events_from_day = sorted(events_from_day, key=attrgetter("start_date"))
        events_html = ""
        for i, event in enumerate(events_from_day):
            # reset event_dict to empty at the beggining of each week
            if wday == 6:
                self.event_dict = {}

            # check if the current event has been processed in a previous day this week
            # if it has, set the order to whatever it was set to previously
            # it it hasn't set the order to the order from this day for future days
            if event.id in self.event_dict:
                order = self.event_dict[event.id]
            else:
                self.event_dict[event.id] = i + empty_rows  # set the order for future days
                order = 0  # order for this day stays the same. it will go directly below the previous event for the day

            # the the set order is different from the current loop order, add as many empty rows as required to make
            # the events line up when viewed side by side
            if order != i + empty_rows:
                for _ in range(order):
                    empty_rows += 1
                    events_html += f"<tr><td><span class='calendar-event-hidden'>{event.user.username}</span></td></tr>"

            # event is a single day event
            events_html += "<tr><td class='day-table-cell'>"
            if event.is_single_day_event():
                events_html += f'<a class="calendar-event single-day-event" href="{event.get_absolute_url()}">{event.user.username.title()}</a>'
            # event is a multi-day event and the start date is the same as the current day being rendered
            elif event.start_date.day == day:
                if event.event_length_days() == 2 \
                        or event.event_length_days() > 5 or day == 1 or day == last_day_of_month:
                    events_html += f'<a class="calendar-event multi-day-start" href="{event.get_absolute_url()}">{event.user.username.title()}</a>'
                else:
                    events_html += f'<a class="calendar-event multi-day-start" href="{event.get_absolute_url()}"></a>'
            elif event.start_date < date < event.end_date:
                middle = event.event_length_days() // 2
                middle_day = (event.start_date + datetime.timedelta(days=middle)).day
                if day == middle_day or day == 1 or day == last_day_of_month:
                    events_html += f'<a class="calendar-event multi-day-middle" href="{event.get_absolute_url()}">{event.user.username.title()}</a>'
                else:
                    events_html += f'<a class="calendar-event multi-day-middle" href="{event.get_absolute_url()}"></a>'
            elif event.end_date.day == day:
                if event.event_length_days() == 2 \
                        or event.event_length_days() > 5 or day == last_day_of_month or day == 1:
                    events_html += f'<a class="calendar-event multi-day-end" href="{event.get_absolute_url()}">{event.user.username.title()}</a>'
                else:
                    events_html += f'<a class="calendar-event multi-day-end" href="{event.get_absolute_url()}"></a>'
            events_html += "</td></tr>"

        holidays_html = ""

        if date.month != themonth:
            string = f"<td height=150 valign='top' class='noday {self.cssclasses[wday]}'>"
        else:
            string = f"<td height=150 valign='top' class='{self.cssclasses[wday]}'>"

        for d, holiday_name in ontario_holidays:
            if date == d:
                holidays_html = f"<span class='canada-holiday'>&nbsp;{holiday_name}</span>"
                string = f"<td height=150 valign='top' class='holiday {self.cssclasses[wday]}'>"

        string += "<table class='day-table'><tbody>"

        if date == today:
            string += "<tr><td class='today day-of-month'>"
            string += f"<a href='{reverse('vacation:add', kwargs={'year': date.year, 'month': date.month, 'day': date.day})}' class='today'>{day}</a>"
        else:
            string += "<tr><td class='day-of-month'>"
            string += f"<a href='{reverse('vacation:add', kwargs={'year': date.year, 'month': date.month, 'day': date.day})}'>{day}</a>"

        string += f"{holidays_html}"
        string += "</td></tr>"
        string += f"{events_html}"
        string += "</tbody></table></td>"

        return string

    def formatweekday(self, day):
        """
        Return a weekday name as a table header.
        """
        return '<th class="%s-header">%s</th>' % (self.cssclasses[day], day_abbr[day])

    def formatweek(self, theyear, themonth, theweek, events):
        s = ''.join(self.formatday(theyear, themonth, date, events) for date in theweek)
        return f"<tr>{s}</tr>"

    def formatweekheader(self):
        """
        Return a header for a week as a table row.
        """
        s = ''.join(self.formatweekday(i) for i in self.iterweekdays())
        return '<tr class="week-header">%s</tr>' % s

    def formatmonthname(self, theyear, themonth, withyear=True):
        """
        Return a month name as a table row.
        """
        if withyear:
            s = '%s %s' % (month_name[themonth], theyear)
        else:
            s = '%s' % month_name[themonth]
        return '<tr><th colspan="7" class="month-name">%s</th></tr>' % s

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
        for week in self.monthdatescalendar(theyear, themonth):
            a(self.formatweek(theyear, themonth, week, events))
            a('\n')
        # a("<\table>")
        a("\n")
        return ''.join(table)
