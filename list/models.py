from django.contrib.auth.models import User
from django.core import validators
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.shortcuts import reverse
from django.utils import timezone
from ordered_model.models import OrderedModel


class Customer(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name.title()}"


class Machine(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def get_ordered_jobs(self):
        jobs = []
        mo = self.get_ordering_queryset()
        for order in mo:
            jobs.append(order.job)

        return jobs

    def get_ordering_queryset(self):
        return (
            MachineOrder.objects.filter(machine=self)
            .filter(job__active=True)
            .order_by("order")
        )

    def max_order(self):
        mo = (
            MachineOrder.objects.filter(machine=self)
            .filter(job__active=True)
            .order_by("order")
            .last()
        )
        if not mo:
            return 0
        return mo.order

    def active_jobs(self):
        return (
            Job.objects.filter(active=True)
            .filter(details__machine__pk=self.pk)
            .distinct()
        )

    def inactive_jobs(self):
        return (
            Job.objects.filter(active=False)
            .filter(details__machine__pk=self.pk)
            .distinct()
        )

    def __str__(self):
        return f"{self.name}"


class Job(models.Model):
    YES = "Y"
    NO = "N"
    NA = "-"
    SETUP_SHEETS_CHOICES = [
        (YES, "Yes"),
        (NO, "No"),
        (NA, "N/A"),
    ]

    job_number = models.PositiveIntegerField(
        validators=[
            validators.MinValueValidator(1000),
            validators.MaxValueValidator(9999),
        ]
    )
    description = models.CharField(max_length=50, blank=True)
    add_tools = models.BooleanField(default=True)
    setup_sheets = models.CharField(
        max_length=1, choices=SETUP_SHEETS_CHOICES, default=NO, blank=True
    )
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE)
    date_added = models.DateField(default=timezone.now, blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    datetime_completed = models.DateTimeField(default=None, blank=True, null=True)
    active = models.BooleanField(blank=True, default=True)

    def up(self, machine):
        MachineOrder.objects.get(machine=machine, job=self).up()

    def down(self, machine):
        MachineOrder.objects.get(machine=machine, job=self).down()

    def to(self, machine, order):
        MachineOrder.objects.get(machine=machine, job=self).to(order)

    def order(self, machine):
        return MachineOrder.objects.get(machine=machine, job=self).order

    def using_machines(self):
        job = Job.objects.get(job_number=self.job_number)
        details = Detail.objects.filter(job=job)
        machines = [detail.machine for detail in details]
        return machines

    def change_machine(self, original_machine, new_machine):
        details = self.details.filter(machine=original_machine)
        for d in details:
            d.machine = new_machine
            d.save()

    def details_for_machine(self, machine):
        details = Detail.objects.filter(job=self, machine=machine)
        count = 0
        for detail in details:
            count += detail.quantity

        return count

    def get_absolute_url(self):
        return reverse("list:job-detail", args=[self.pk])

    def save(self, **kwargs):
        self.full_clean()
        super().save(**kwargs)

    def __str__(self):
        return f"{self.job_number} {self.description}"


class MachineOrder(models.Model):
    machine = models.ForeignKey(
        Machine, related_name="machine_order", on_delete=models.CASCADE
    )
    job = models.ForeignKey(Job, related_name="machine_order", on_delete=models.CASCADE)
    order = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["machine", "job"], name="unique_order")
        ]

    def up(self):
        order = self.order - 1
        if order < 1:
            return
        old_job = MachineOrder.objects.get(machine=self.machine, order=order)
        self.order = order
        self.save()
        old_job.order += 1
        old_job.save()

    def down(self):
        max_order = self.machine.max_order()
        order = self.order + 1
        if order > max_order:
            return
        old_job = MachineOrder.objects.get(machine=self.machine, order=order)
        self.order = order
        self.save()
        old_job.order -= 1
        old_job.save()

    def to(self, order):
        # moving down
        if order > self.order:
            if order > self.machine.max_order():
                return
            for i in range(self.order, order + 1):
                if i != self.order:
                    mo = MachineOrder.objects.get(machine=self.machine, order=i)
                    mo.order -= 1
                    mo.save()
            self.order = order
            self.save()

        # moving up
        if order < self.order:
            if order < 1:
                return
            # move in reverse order so only one object exists for a given order value
            for i in range(self.order - 1, order - 1, -1):
                mo = MachineOrder.objects.get(machine=self.machine, order=i)
                mo.order += 1
                mo.save()
            self.order = order
            self.save()

    def __repr__(self):
        return f"[{self.machine.name}] - [{self.job.job_number}] - <{self.order}>"


class Detail(models.Model):
    job = models.ForeignKey(
        Job, on_delete=models.CASCADE, related_name="details", blank=False
    )
    ltd_item_number = models.IntegerField(blank=False)
    outsource_detail_number = models.CharField(max_length=24, blank=False)
    quantity = models.PositiveIntegerField(blank=False)
    description = models.CharField(max_length=64, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["job", "ltd_item_number"], name="unique_item"
            ),
            models.UniqueConstraint(
                fields=["job", "outsource_detail_number"], name="unique_detail"
            ),
        ]

    machine = models.ForeignKey(
        Machine, on_delete=models.CASCADE, blank=True, null=True, related_name="details"
    )

    original_machine = models.ForeignKey(
        Machine, on_delete=models.CASCADE, blank=True, null=True
    )

    def get_absolute_url(self, *args, **kwargs):
        return reverse("list:detail", args=[self.pk])

    def save(self, *args, **kwargs):
        if self.original_machine is None and self.machine is not None:
            try:
                mo = MachineOrder.objects.get(job=self.job, machine=self.machine)
            except MachineOrder.DoesNotExist:
                order = self.machine.max_order() + 1
                MachineOrder.objects.create(
                    job=self.job, machine=self.machine, order=order
                )

        elif self.original_machine != self.machine:
            # check if MachineOrder exists for self.machine and self.job,
            # if not create it
            new_order = self.machine.max_order() + 1
            new_mo, created = MachineOrder.objects.get_or_create(
                job=self.job, machine=self.machine
            )
            if created:
                new_mo.order = new_order
                new_mo.save()

            # check if any details still exist for self.original_machine and
            # self.job, if not delete the old MachineOrder object
            # if MachineOrder object is deleted, check if any machine order
            # objects exist with a higher order and move them up
            old_machine_jobs_detail_count = (
                self.job.details.filter(machine=self.original_machine)
                .exclude(pk=self.pk)
                .count()
            )

            if old_machine_jobs_detail_count == 0:
                old_mo = MachineOrder.objects.get(
                    job=self.job, machine=self.original_machine
                )
                old_mo.delete()

        self.original_machine = self.machine
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        job = self.job
        super().delete(*args, **kwargs)
        if job.details.count() == 0:
            job.delete()

    def __str__(self):
        return f"[{self.job.job_number}] - Item {self.ltd_item_number}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    machines = models.ManyToManyField(Machine)

    def get_absolute_url(self):
        return reverse("list:profile", args=[self.pk])

    def __str__(self):
        return f"{self.user.username}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        p = Profile.objects.create(user=instance)
        instance.profile = p
        instance.save()


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_delete, sender=MachineOrder)
def delete(sender, instance, **kwargs):
    order = instance.order
    mo = instance.machine.get_ordering_queryset()
    for moi in mo:
        if moi.order > order:
            moi.order -= 1
            moi.save()


# @receiver(post_save, sender=Detail)
# def create_machine_order(sender, instance, created, **kwargs):
#     if created and instance.job not in [
#         x.job for x in MachineOrder.objects.filter(machine=instance.machine)
#     ] and instance.machine is not None:
#         order = instance.machine.max_order() + 1
#         mo = MachineOrder.objects.create(
#             machine=instance.machine, job=instance.job, order=order
#         )
