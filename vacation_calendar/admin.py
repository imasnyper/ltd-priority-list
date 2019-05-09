from django.contrib import admin

from vacation_calendar.models import Vacation


class VacationAdmin(admin.ModelAdmin):
    list_display = ['user', 'start_date', 'end_date']


admin.site.register(Vacation, VacationAdmin)
