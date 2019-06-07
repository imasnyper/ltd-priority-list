from django.test import TestCase

from list.models import Job, Customer, Machine


class JobModelTestCase(TestCase):
    def setUp(self):
        pin1 = Machine.objects.create(name="Pinnacle 1")
        pin2 = Machine.objects.create(name="Pinnacle 2")
        starvision = Machine.objects.create(name="Starvision")

        c1 = Customer.objects.create(name="Custy 1")
        c2 = Customer.objects.create(name="ABC Co.")

        Job.objects.create(job_number=1234, description="test job 1", machine=pin1, customer=c1, add_tools=True)
        Job.objects.create(job_number=4567, description="test job 2", machine=pin1, customer=c2, add_tools=False)
        Job.objects.create(job_number=7890, description="test job 3", machine=pin1, customer=c1, add_tools=True)
        Job.objects.create(job_number=6321, description="test job 4", machine=pin2, customer=c1, add_tools=False)
        Job.objects.create(job_number=4321, description="test job 5", machine=pin2, customer=c2, add_tools=True)
        Job.objects.create(job_number=7654, description="test job 6", machine=pin2, customer=c2, add_tools=False)
        Job.objects.create(job_number=8523, description="test job 7", machine=starvision, customer=c1, add_tools=True)
        Job.objects.create(job_number=7412, description="test job 8", machine=starvision, customer=c2, add_tools=False)

    def test_str(self):
        j = Job.objects.first()
        self.assertEqual(str(j), f"{j.job_number} {j.description}")

    def test_find_max_order(self):
        j = Job.objects.first()
        max = j._find_max_order()
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
        self.assertEqual(j.order, j._find_max_order(exclude_self=True))

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
        j = Job.objects.first()
        self.assertTrue(j.active)
        j.active = False
        j.save()

        self.assertFalse(j.active)
        j.active = True
        j.save()

        queryset = Job.objects.filter(active=True, machine=j.machine)
        order_list = [job.order for job in queryset]
        expected_list = [i for i in range(queryset.count())]

        self.assertTrue(j.active)
        self.assertListEqual(order_list, expected_list)
        self.assertEqual(j.datetime_completed, None)

    def test_change_job_machine(self):
        m1 = Machine.objects.first()
        m2 = Machine.objects.last()
        j = Job.objects.filter(machine=m1).first()
        j.machine = m2
        j.save()

        old_queryset = Job.objects.filter(active=True, machine=m1)
        old_order_list = [job.order for job in old_queryset]
        old_expected_list = [i for i in range(old_queryset.count())]

        new_queryset = Job.objects.filter(active=True, machine=m2)
        new_order_list = [job.order for job in new_queryset]
        new_expected_list = [i for i in range(new_queryset.count())]

        self.assertListEqual(old_order_list, old_expected_list)
        self.assertListEqual(new_order_list, new_expected_list)