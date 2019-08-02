# import pdb

from django.contrib.auth.models import User
from django.core import validators
from django.db import models
from django.db.models import Max
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import reverse
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
    YES = "Y"
    NO = "N"
    NA = "-"
    SETUP_SHEETS_CHOICES = [
        (YES, "Yes"),
        (NO, "No"),
        (NA, "N/A"),
    ]

    job_number = models.PositiveIntegerField(
        validators=[validators.MinValueValidator(1000),
                    validators.MaxValueValidator(9999)])
    description = models.CharField(max_length=50)
    add_tools = models.BooleanField()
    setup_sheets = models.CharField(max_length=1, choices=SETUP_SHEETS_CHOICES,
                                    default=NO, blank=True)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    machine = models.ForeignKey("Machine", on_delete=models.CASCADE)
    date_added = models.DateField(
        default=timezone.now, blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    datetime_completed = models.DateTimeField(default=None, blank=True,
                                              null=True)
    order_with_respect_to = 'machine'
    active = models.BooleanField(blank=True, default=True)

    def get_absolute_url(self):
        return reverse("list:job-detail", args=[self.pk])

    def _find_max_order(self, include_self=False):
        """
        get the max order for the ordering_queryset
        :return: int - max order
        """
        oq = self.get_ordering_queryset()
        if include_self:
            last = (oq
                    .filter(active=True)
                    .aggregate(Max('order'))
                    .get('order__max')
                    )
        else:
            last = (oq
                    .filter(active=True)
                    .exclude(id=self.id)
                    .aggregate(Max('order'))
                    .get('order__max')
                    )

        if last is None:
            last = -1

        return last

    def _bot(self):
        """
        find the max order of the destination ordering_queryset and set the
        instance order to one greater.
        it this method does not change the order of any other instance in the
        set. meant to be used only
        from within the save method for setting the order of an instance that
        just changed machines.
        :return: None
        """
        last = self._find_max_order()

        self.order = last + 1
        self.save()

    def save(self, *args, **kwargs):
        # If this instance is being created for the first time, old instance
        # won't exist
        try:
            old_job = Job.objects.get(id=self.pk)
            super().save(*args, **kwargs)
            self._save(old_job, *args, **kwargs)
        except Job.DoesNotExist:
            super().save(*args, **kwargs)

    def _save(self, old_job, *args, **kwargs):
        if old_job is not None:
            if old_job.active and not self.active:
                smooth_ordering(old_job)
                self.order = 0
                self.datetime_completed = timezone.now()
                super().save(*args, **kwargs)
            elif not old_job.active and self.active:
                order = self._find_max_order()
                self.datetime_completed = None
                self.order = order + 1
                super().save(*args, **kwargs)

            if self.machine.pk != old_job.machine.pk:
                # If machine changed, the instance is switching to a
                # different subset,
                # we need to send that instance to the bottom of that subset.
                # NOTE: not overriding ordered_model's bottom method,
                # since that uses the to() method
                # to assign the order for the object, and that messes up the
                # order of the machine the job is
                # being moved to.
                self._bot()

                # If there were objects after the instance in the OLD subset,
                # move them up in the order by 1 each
                smooth_ordering(old_job)

    class Meta(OrderedModel.Meta):
        pass

    def __str__(self):
        return f"{self.job_number} {self.description}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    machines = models.ManyToManyField(Machine)

    def get_absolute_url(self):
        return reverse("list:profile", args=[self.pk])

    def __str__(self):
        return f"{self.user.username}"


def smooth_ordering(instance):
    """
    move every job after the given instance up by 1 in the ordering
    :param instance: the instance that changed machines or was archived
    :return: None
    """
    # If there were objects after the instance in the OLD subset, move them
    # up in the order by 1 each
    order = instance.order + 1
    try:
        while True:
            job = Job.objects.get(machine=instance.machine, order=order,
                                  active=True)
            job.to(order - 1)
            order += 1
    except Job.DoesNotExist:
        pass


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
