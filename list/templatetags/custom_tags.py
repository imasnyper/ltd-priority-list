from django import template
from django.shortcuts import get_object_or_404

from list.models import Job, Machine, MachineOrder

register = template.Library()


def order(job, machine):
    job = get_object_or_404(Job, job_number=job.job_number)
    machine = get_object_or_404(Machine, pk=machine)
    machine_order = get_object_or_404(MachineOrder, job=job, machine=machine)

    return machine_order.order


def all_job_details(job):
    return job.details.count()


def details_for_machine(job, machine):
    return job.details_for_machine(machine)


def job_machines(job):
    machines = job.using_machines()
    machines_string = ", ".join([str(m) for m in machines])
    return machines_string


register.filter("order", order)
register.filter("details_for_machine", details_for_machine)
register.filter("job_machines", job_machines)
register.filter("all_job_details", all_job_details)
