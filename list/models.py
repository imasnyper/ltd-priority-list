# import pdb

from django.core import validators
from django.db import models
from django.db.models import Max
from django.utils import timezone
from ordered_model.models import OrderedModel


class Customer(OrderedModel):
    name = models.CharField(max_length=50, unique=True)

    class Meta(OrderedModel.Meta):
        ordering = ('name',)

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name.title()}"


class Machine(OrderedModel):
    name = models.CharField(max_length=50, unique=True)

    def active_jobs(self):
        return Job.objects.filter(machine__pk=self.pk).filter(active=True)

    def inactive_jobs(self):
        return Job.objects.filter(machine__pk=self.pk).filter(active=False)

    class Meta(OrderedModel.Meta):
        ordering = ("order",)

    def __str__(self):
        return f"{self.name}"


class Job(OrderedModel):
    job_number = models.PositiveIntegerField(
        validators=[validators.MinValueValidator(1000),
                    validators.MaxValueValidator(9999)])
    description = models.CharField(max_length=50)
    add_tools = models.BooleanField()
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    machine = models.ForeignKey("Machine", on_delete=models.CASCADE)
    date_added = models.DateField(
        default=timezone.now, blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    datetime_completed = models.DateTimeField(default=None, blank=True, null=True)
    order_with_respect_to = 'machine'
    active = models.BooleanField(blank=True, null=True, default=True)

    def bot(self):
        # Looks for the max value for 'order' in a given subset, or -1(we add 1 before assigning the value)
        # if the subset is empty
        oq = self.get_ordering_queryset()
        last = (oq
                .exclude(id=self.id)
                .aggregate(Max('order'))
                .get('order__max')
                or -1)

        self.order = last + 1
        self.save()

    def save(self, *args, **kwargs):
        # If this instance is being created for the first time, old instance won't exist
        try:
            old_job = Job.objects.get(id=self.pk)
        except Job.DoesNotExist:
            old_job = None

        if not self.active:
            self.datetime_completed = timezone.now()

        super().save(*args, **kwargs)

        if old_job is not None and self.machine.pk != old_job.machine.pk:
            # If machine changed, the instance is switching to a different subset,
            # we need to send that instance to the bottom of that subset.
            # NOTE: not overriding ordered_model's bottom method, since that uses the to() method
            # to assign the order for the object, and that messes up the order of the machine the job is
            # being moved to.
            self.bot()

            try:
                # If there were objects after the instance in the OLD subset, move them up in the order by 1 each
                order = old_job.order + 1
                while True:
                    job = Job.objects.get(machine=old_job.machine, order=order)
                    job.to(order - 1)
                    order += 1
            except Job.DoesNotExist:
                pass

    class Meta(OrderedModel.Meta):

        pass

    def __str__(self):
        return f"{self.job_number} {self.description}"
