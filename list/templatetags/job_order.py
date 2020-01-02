from django import template
from django.shortcuts import get_object_or_404

from list.models import Job, Machine, MachineOrder

register = template.Library()


def order(job, machine):
    job = get_object_or_404(Job, job_number=job.job_number)
    machine = get_object_or_404(Machine, pk=machine)
    machine_order = get_object_or_404(MachineOrder, job=job, machine=machine)

    return machine_order.order


register.filter("order", order)
