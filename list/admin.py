from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin

from list.models import Customer, Job, Machine, Profile


# Register your models here.


class JobAdmin(OrderedModelAdmin):
    list_display = ('job_number', 'description', 'customer',
                    'machine', 'move_up_down_links')
    ordering = ("machine__order", "order",)


class MachineAdmin(OrderedModelAdmin):
    list_display = ("name", "move_up_down_links")
    ordering = ("order",)


admin.site.register(Job, JobAdmin)
admin.site.register(Customer)
admin.site.register(Machine, MachineAdmin)
admin.site.register(Profile)
