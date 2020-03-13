from itertools import cycle

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APITestCase

from list.models import Machine, Profile, Customer, Job
from list.tests.util import create_jobs, create_details


class BaseTestCase(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username="testuser1", password="testing123")

        self.c1 = Customer.objects.create(name="c1")
        self.c2 = Customer.objects.create(name="c2")

        self.j1 = Job.objects.create(job_number=1111, customer=self.c1)
        self.j2 = Job.objects.create(job_number=2222, customer=self.c2)

        self.m1 = Machine.objects.create(name="Pinnacle 1")
        self.m2 = Machine.objects.create(name="Pinnacle 2")
        self.m3 = Machine.objects.create(name="Starvision")


class ViewTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.p1 = Profile.objects.get(user=self.u1)
        self.p1.machines.set([self.m1, self.m2])
        self.p1.save()

        self.c3 = Customer.objects.create(name="Custy 1")
        self.c4 = Customer.objects.create(name="ABC Co.")

        # create referenced jobs for using in testing
        create_jobs(15, [self.c1, self.c2])

        jobs = Job.objects.all()
        machines = cycle(list(Machine.objects.all()))

        for job in jobs:
            create_details(5, job, next(machines))


class CustomAPITestCase(BaseTestCase, APITestCase):
    pass
