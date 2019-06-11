from django.test import TestCase

from list.models import Job, Customer, Machine
from list.tests.util import create_jobs


class JobModelTestCase(TestCase):
    def setUp(self):
        self.pin1 = Machine.objects.create(name="Pinnacle 1")
        self.pin2 = Machine.objects.create(name="Pinnacle 2")
        self.starvision = Machine.objects.create(name="Starvision")

        self.c1 = Customer.objects.create(name="Custy 1")
        self.c2 = Customer.objects.create(name="ABC Co.")

        self.j1 = create_jobs(3, self.pin1, [self.c1, self.c2])
        self.j2 = create_jobs(3, self.pin2, [self.c1, self.c2])
        self.j3 = create_jobs(3, self.starvision, [self.c1, self.c2])

    def test_str(self):
        j = Job.objects.first()
        self.assertEqual(str(j), f"{j.job_number} {j.description}")

    def test_find_max_order(self):
        j = Job.objects.first()
        max = j._find_max_order() + 1
        self.assertEqual(max, Job.objects.filter(active=True, machine=j.machine).count() - 1)

    def test_save_new_job(self):
        j = Job.objects.create(
            job_number=6543,
            description="test new job",
            machine=Machine.objects.first(),
            customer=Customer.objects.first(),
            add_tools=True
        )

        self.assertTrue(j.active)
        self.assertEqual(j.order, j._find_max_order(include_self=True))

    def test_deactivate_job(self):
        j = Job.objects.first()
        j.active = False
        j.save()

        queryset = Job.objects.filter(active=True, machine=j.machine)
        order_list = [job.order for job in queryset]
        expected_list = [i for i in range(queryset.count())]

        self.assertFalse(j.active)
        self.assertNotEqual(j.datetime_completed, None)
        self.assertListEqual(order_list, expected_list)

    def test_reactivate_job(self):
        # first deactivate an active job and save it to the database
        j = Job.objects.first()
        self.assertTrue(j.active)
        j.active = False
        j.save()

        # then reactivate and save the job
        self.assertFalse(j.active)
        j.active = True
        j.save()

        queryset = Job.objects.filter(active=True, machine=j.machine)
        order_list = [job.order for job in queryset]
        expected_list = [i for i in range(queryset.count())]

        self.assertTrue(j.active)
        self.assertListEqual(order_list, expected_list)
        self.assertEqual(j.datetime_completed, None)
        self.assertEqual(j.order, len(order_list) - 1)

    def test_change_job_machine(self):
        j = self.j1
        j.machine = self.pin2
        j.save()

        old_queryset = Job.objects.filter(active=True, machine=self.pin1)
        old_order_list = [job.order for job in old_queryset]
        old_expected_list = [i for i in range(old_queryset.count())]

        new_queryset = Job.objects.filter(active=True, machine=self.pin2)
        new_order_list = [job.order for job in new_queryset]
        new_expected_list = [i for i in range(new_queryset.count())]

        self.assertListEqual(old_order_list, old_expected_list)
        self.assertListEqual(new_order_list, new_expected_list)


class MachineModelTestCase(TestCase):
    def setUp(self):
        self.pin1 = Machine.objects.create(name="Pinnacle 1")
        self.pin2 = Machine.objects.create(name="Pinnacle 2")
        self.starvision = Machine.objects.create(name="Starvision")

        self.c1 = Customer.objects.create(name="Custy 1")
        self.c2 = Customer.objects.create(name="ABC Co.")

        self.j1 = create_jobs(3, self.pin1, [self.c1, self.c2])
        self.j2 = create_jobs(3, self.pin1, [self.c1, self.c2])
        self.j3 = create_jobs(3, self.pin1, [self.c1, self.c2])

    def test_active_jobs(self):
        self.j3.active = False
        self.j3.save()

        self.assertListEqual(list(self.pin1.active_jobs()), list(Job.objects.filter(machine__pk=self.pin1.pk, active=True)))

    def test_inactive_jobs(self):
        self.j3.active = False
        self.j3.save()

        self.assertEqual(list(self.pin1.active_jobs()), list(Job.objects.filter(machine__pk=self.pin1.pk, active=True)))