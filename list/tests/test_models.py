from django.test import TestCase

from list.models import *


class CustomTestCase(TestCase):
    def setUp(self):
        self.c1 = Customer.objects.create(name="c1")
        self.c2 = Customer.objects.create(name="c2")

        self.j1 = Job.objects.create(job_number=1111, customer=self.c1)
        self.j2 = Job.objects.create(job_number=2222, customer=self.c2)

        self.m1 = Machine.objects.create(name="m1")
        self.m2 = Machine.objects.create(name="m2")


class JobModelTestCase(CustomTestCase):
    def test_str(self):
        j = Job.objects.first()
        self.assertEqual(str(j), f"{j.job_number} {j.description}")

    def test_delete_job_cascade(self):
        d1 = Detail.objects.create(
            job=self.j1, machine=self.m1, ltd_item_number=1, outsource_detail_number=10
        )
        d2 = Detail.objects.create(
            job=self.j2, machine=self.m2, ltd_item_number=1, outsource_detail_number=10
        )

        self.assertNotEqual(MachineOrder.objects.count(), 0)
        self.assertNotEqual(Detail.objects.count(), 0)
        self.assertNotEqual(Job.objects.count(), 0)

        self.j1.delete()
        self.j2.delete()

        self.assertEqual(Job.objects.count(), 0)
        self.assertEqual(Job.objects.count(), 0)
        self.assertEqual(Job.objects.count(), 0)


class DetailModelTestCase(CustomTestCase):
    def setUp(self):
        super().setUp()
        self.j3 = Job.objects.create(job_number=3333, customer=self.c1)

    def test_create_detail(self):
        # check that no MachineOrder objects exist
        self.assertEqual(MachineOrder.objects.count(), 0)

        # create 2 Detail objects of the same job on the same machine
        # check that there's only 1 MachineOrder object
        # and the order is 1
        d = Detail.objects.create(
            job=self.j1, machine=self.m1, ltd_item_number=1, outsource_detail_number=10
        )
        d2 = Detail.objects.create(
            job=self.j1, machine=self.m1, ltd_item_number=2, outsource_detail_number=20
        )
        self.assertEqual(MachineOrder.objects.count(), 1)
        mo = MachineOrder.objects.get(job=d.job, machine=d.machine)
        self.assertEqual(mo.order, 1)

        # create a new detail of the same job for a different machine
        # check that there are 1 MachineOrder objects for each machine
        d3 = Detail.objects.create(
            job=self.j1, machine=self.m2, ltd_item_number=3, outsource_detail_number=30
        )
        self.assertEqual(
            MachineOrder.objects.filter(job__active=True)
            .filter(machine=self.m1)
            .count(),
            1,
        )
        self.assertEqual(
            MachineOrder.objects.filter(job__active=True)
            .filter(machine=self.m2)
            .count(),
            1,
        )

        # create another new detail for a different job on the second machine
        # check that there are now 2 machine order objects for the second machine
        # and the order for the first job is 1 and the order for the second job is 2
        d4 = Detail.objects.create(
            job=self.j2, machine=self.m2, ltd_item_number=1, outsource_detail_number=10
        )
        self.assertEqual(
            MachineOrder.objects.filter(job__active=True)
            .filter(machine=self.m2)
            .count(),
            2,
        )
        mo = MachineOrder.objects.get(job=self.j1, machine=self.m2)
        mo2 = MachineOrder.objects.get(job=self.j2, machine=self.m2)
        self.assertEqual(mo.order, 1)
        self.assertEqual(mo2.order, 2)

    def test_delete_detail(self):
        d1 = Detail.objects.create(
            job=self.j1, machine=self.m1, ltd_item_number=1, outsource_detail_number=10
        )
        d2 = Detail.objects.create(
            job=self.j1, machine=self.m1, ltd_item_number=2, outsource_detail_number=20
        )

        self.assertEqual(MachineOrder.objects.count(), 1)

        d1.delete()

        self.assertEqual(MachineOrder.objects.count(), 1)

        d2.delete()

        # check that job and MachineOrder objects are deleted upon final detail deletion
        self.assertEqual(MachineOrder.objects.count(), 0)
        self.assertEqual(Job.objects.count(), 2)
        self.assertEqual(MachineOrder.objects.count(), 0)

    def test_delete_order_change(self):
        d1 = Detail.objects.create(
            job=self.j1, machine=self.m1, ltd_item_number=1, outsource_detail_number=10
        )
        d2 = Detail.objects.create(
            job=self.j2, machine=self.m1, ltd_item_number=1, outsource_detail_number=10
        )
        j3 = Job.objects.create(job_number=3333, customer=self.c1)
        d3 = Detail.objects.create(
            job=j3, machine=self.m1, ltd_item_number=1, outsource_detail_number=10
        )

        mo1 = MachineOrder.objects.get(job=d1.job, machine=d1.machine)
        mo2 = MachineOrder.objects.get(job=d2.job, machine=d2.machine)
        mo3 = MachineOrder.objects.get(job=d3.job, machine=d3.machine)

        d2.delete()

        mo1 = MachineOrder.objects.get(job=d1.job, machine=d1.machine)
        mo3 = MachineOrder.objects.get(job=d3.job, machine=d3.machine)

        self.assertEqual(mo1.order, 1)
        self.assertEqual(mo3.order, 2)

    def test_machine_change_order_update(self):
        d1 = Detail.objects.create(
            job=self.j1, machine=self.m1, ltd_item_number=1, outsource_detail_number=10
        )
        d2 = Detail.objects.create(
            job=self.j2, machine=self.m1, ltd_item_number=1, outsource_detail_number=10
        )
        d3 = Detail.objects.create(
            job=self.j3, machine=self.m1, ltd_item_number=1, outsource_detail_number=10
        )

        d1.machine = self.m2
        d1.save()

        mo1 = MachineOrder.objects.get(job=d1.job, machine=d1.machine)
        mo2 = MachineOrder.objects.get(job=d2.job, machine=d2.machine)
        mo3 = MachineOrder.objects.get(job=d3.job, machine=d3.machine)

        self.assertEqual(mo1.machine, self.m2)
        self.assertEqual(mo1.order, 1)

        mo = self.m1.get_ordering_queryset()
        moo = [moi.order for moi in mo]

        self.assertListEqual(moo, [1, 2])
        self.assertEqual(mo2.order, 1)
        self.assertEqual(mo3.order, 2)


class MachineOrderTestCase(CustomTestCase):
    def setUp(self):
        super().setUp()
        self.j3 = Job.objects.create(job_number=3333, customer=self.c1)
        self.j4 = Job.objects.create(job_number=4444, customer=self.c1)
        self.j5 = Job.objects.create(job_number=5555, customer=self.c1)
        self.d1 = Detail.objects.create(
            job=self.j1, machine=self.m1, ltd_item_number=1, outsource_detail_number=10
        )
        self.d2 = Detail.objects.create(
            job=self.j2, machine=self.m1, ltd_item_number=1, outsource_detail_number=10
        )
        self.d3 = Detail.objects.create(
            job=self.j3, machine=self.m1, ltd_item_number=1, outsource_detail_number=10
        )
        self.d4 = Detail.objects.create(
            job=self.j4, machine=self.m1, ltd_item_number=1, outsource_detail_number=10
        )
        self.d5 = Detail.objects.create(
            job=self.j5, machine=self.m1, ltd_item_number=1, outsource_detail_number=10
        )

    def test_machine_order_up(self):
        mo2 = MachineOrder.objects.get(job=self.d2.job, machine=self.d2.machine)

        mo = MachineOrder.objects.filter(machine=self.d1.machine)
        moo = [moi.order for moi in mo]

        self.assertListEqual(moo, [1, 2, 3, 4, 5])

        mo2.up()

        mo = MachineOrder.objects.filter(machine=self.d1.machine).order_by("order")
        moo = [moi.order for moi in mo]

        self.assertListEqual(moo, [1, 2, 3, 4, 5])

        mo1 = MachineOrder.objects.get(job=self.d1.job, machine=self.d1.machine)
        mo2 = MachineOrder.objects.get(job=self.d2.job, machine=self.d2.machine)
        mo3 = MachineOrder.objects.get(job=self.d3.job, machine=self.d3.machine)

        self.assertEqual(mo1.order, 2)
        self.assertEqual(mo2.order, 1)
        self.assertEqual(mo3.order, 3)

    def test_machine_order_down(self):
        mo2 = MachineOrder.objects.get(job=self.d2.job, machine=self.d2.machine)

        mo = MachineOrder.objects.filter(machine=self.d1.machine)
        moo = [moi.order for moi in mo]

        self.assertListEqual(moo, [1, 2, 3, 4, 5])

        mo2.down()

        mo = MachineOrder.objects.filter(machine=self.d1.machine).order_by("order")
        moo = [moi.order for moi in mo]

        self.assertListEqual(moo, [1, 2, 3, 4, 5])

        mo1 = MachineOrder.objects.get(job=self.d1.job, machine=self.d1.machine)
        mo2 = MachineOrder.objects.get(job=self.d2.job, machine=self.d2.machine)
        mo3 = MachineOrder.objects.get(job=self.d3.job, machine=self.d3.machine)

        self.assertEqual(mo1.order, 1)
        self.assertEqual(mo2.order, 3)
        self.assertEqual(mo3.order, 2)

    def test_machine_order_to_down(self):
        mo2 = MachineOrder.objects.get(job=self.d2.job, machine=self.d2.machine)

        mo = MachineOrder.objects.filter(machine=self.d1.machine).order_by("order")
        moo = [moi.order for moi in mo]

        self.assertListEqual(moo, [1, 2, 3, 4, 5])

        mo2.to(4)

        mo = MachineOrder.objects.filter(machine=self.d1.machine).order_by("order")
        moo = [moi.order for moi in mo]

        self.assertListEqual(moo, [1, 2, 3, 4, 5])

        mo1 = MachineOrder.objects.get(job=self.d1.job, machine=self.d1.machine)
        mo2 = MachineOrder.objects.get(job=self.d2.job, machine=self.d2.machine)
        mo3 = MachineOrder.objects.get(job=self.d3.job, machine=self.d3.machine)
        mo4 = MachineOrder.objects.get(job=self.d4.job, machine=self.d4.machine)
        mo5 = MachineOrder.objects.get(job=self.d5.job, machine=self.d5.machine)

        self.assertEqual(mo1.order, 1)
        self.assertEqual(mo2.order, 4)
        self.assertEqual(mo3.order, 2)
        self.assertEqual(mo4.order, 3)
        self.assertEqual(mo5.order, 5)

    def test_machine_order_to_up(self):
        mo4 = MachineOrder.objects.get(job=self.d4.job, machine=self.d4.machine)

        mo = MachineOrder.objects.filter(machine=self.d1.machine).order_by("order")
        moo = [moi.order for moi in mo]

        self.assertListEqual(moo, [1, 2, 3, 4, 5])

        mo4.to(2)

        mo = MachineOrder.objects.filter(machine=self.d1.machine).order_by("order")
        moo = [moi.order for moi in mo]

        self.assertListEqual(moo, [1, 2, 3, 4, 5])

        mo1 = MachineOrder.objects.get(job=self.d1.job, machine=self.d1.machine)
        mo2 = MachineOrder.objects.get(job=self.d2.job, machine=self.d2.machine)
        mo3 = MachineOrder.objects.get(job=self.d3.job, machine=self.d3.machine)
        mo4 = MachineOrder.objects.get(job=self.d4.job, machine=self.d4.machine)
        mo5 = MachineOrder.objects.get(job=self.d5.job, machine=self.d5.machine)

        self.assertEqual(mo1.order, 1)
        self.assertEqual(mo2.order, 3)
        self.assertEqual(mo3.order, 4)
        self.assertEqual(mo4.order, 2)
        self.assertEqual(mo5.order, 5)


class MachineModelTestCase(CustomTestCase):
    def setUp(self):
        super().setUp()
        self.d1 = Detail.objects.create(
            job=self.j1, machine=self.m1, ltd_item_number=1, outsource_detail_number=10
        )
        self.d2 = Detail.objects.create(
            job=self.j2, machine=self.m1, ltd_item_number=1, outsource_detail_number=10
        )

    def test_get_ordered_jobs(self):
        oj = self.m1.get_ordered_jobs()

        self.assertListEqual(oj, [self.j1, self.j2])

    def test_get_ordering_queryset(self):
        oq = self.m1.get_ordering_queryset()
        test_oq = (
            MachineOrder.objects.filter(job__active=True)
            .filter(machine=self.m1)
            .order_by("order")
        )

        self.assertListEqual(list(oq), list(test_oq))

    def test_get_ordered_jobs(self):
        oj = self.m1.get_ordered_jobs()
        test_oq = self.m1.get_ordering_queryset()
        ordered_jobs = []

        for oq in test_oq:
            ordered_jobs.append(oq.job)

        self.assertListEqual(list(oj), ordered_jobs)

    def test_max_order(self):
        self.assertEqual(2, self.m1.max_order())

        self.d1.delete()
        self.d2.delete()

        self.assertEqual(0, self.m1.max_order())
