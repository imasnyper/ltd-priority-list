from django.contrib import admin

from list.models import Customer, Job, Machine, Profile


# Register your models here.


class JobAdmin(admin.ModelAdmin):
    list_display = ("job_number", "description", "customer")


class MachineAdmin(admin.ModelAdmin):
    list_display = ("name",)


admin.site.register(Job, JobAdmin)
admin.site.register(Customer)
admin.site.register(Machine, MachineAdmin)
admin.site.register(Profile)
