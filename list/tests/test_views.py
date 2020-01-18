from itertools import cycle

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from list.models import Machine, Customer, Profile, Job, MachineOrder
from list.tests.util import create_jobs, create_details


class CustomTestCase(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username="testuser1", password="testing123")

        self.pin1 = Machine.objects.create(name="Pinnacle 1")
        self.pin2 = Machine.objects.create(name="Pinnacle 2")
        self.starvision = Machine.objects.create(name="Starvision")

        self.p1 = Profile.objects.get(user=self.u1)
        self.p1.machines.set([self.pin1, self.pin2])
        self.p1.save()

        self.c1 = Customer.objects.create(name="Custy 1")
        self.c2 = Customer.objects.create(name="ABC Co.")

        # create referenced jobs for using in testing
        create_jobs(15, [self.c1, self.c2])

        jobs = Job.objects.all()
        machines = cycle(list(Machine.objects.all()))

        for job in jobs:
            create_details(5, job, next(machines))


class TestPriorityListView(CustomTestCase):
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("list:priority-list"))
        self.assertRedirects(response, "/accounts/login/?next=/")

    def test_view_uses_correct_template_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(reverse("list:priority-list"))

        self.assertEqual(str(response.context["user"]), "testuser1")
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, "list/index.html")

    def test_view_context(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(reverse("list:priority-list"))

        self.assertListEqual(
            list(response.context["machines"]), list(self.p1.machines.all())
        )
        for machine in response.context["machines"]:
            self.assertListEqual(
                list(machine.active_jobs()),
                list(
                    Job.objects.filter(details__machine=machine, active=True).distinct()
                ),
            )
        self.assertListEqual(
            list(response.context["customers"]),
            list(Customer.objects.all().order_by("name")),
        )
        self.assertEqual(
            response.context["form"].get_initial_for_field(
                response.context["form"].fields["active"], "active"
            ),
            True,
        )


class TestArchiveView(CustomTestCase):
    def setUp(self):
        super().setUp()
        jobs = Job.objects.all()
        for job in jobs:
            job.active = False
            job.save()

        profile = Profile.objects.get(user=self.u1)
        profile.machines.set([self.pin1, self.pin2, self.starvision])
        profile.save()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("list:archive-view"))
        self.assertRedirects(response, "/accounts/login/?next=/archive/")

    def test_view_uses_correct_template_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(reverse("list:archive-view"))

        self.assertEqual(str(response.context["user"]), "testuser1")
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, "list/archive.html")

    def test_pagination_is_ten(self):
        login = self.client.login(username="testuser1", password="testing123")

        response = self.client.get(reverse("list:archive-view"))
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertTrue(len(response.context["jobs"]) == 10)

    def test_lists_all_jobs(self):
        login = self.client.login(username="testuser1", password="testing123")

        base_url = reverse("list:archive-view")

        response = self.client.get(base_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["jobs"]), 10)


class TestJobCreateView(CustomTestCase):
    def test_redirect_if_not_logged_in(self):
        response = self.client.post(reverse("list:add", kwargs={"machine_pk": 1}))
        self.assertRedirects(response, "/accounts/login/?next=/job/add/1/")

    def test_view_uses_correct_template_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.post(reverse("list:add", kwargs={"machine_pk": 1}))

        self.assertEqual(str(response.context["user"]), "testuser1")
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, "list/index.html")


class TestJobDetailView(CustomTestCase):
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(
            reverse("list:job-detail", kwargs={"pk": 1, "machine_pk": 1})
        )
        self.assertRedirects(response, "/accounts/login/?next=/job/1/1/")

    def test_view_uses_correct_template_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(
            reverse("list:job-detail", kwargs={"pk": 1, "machine_pk": 1})
        )

        self.assertEqual(str(response.context["user"]), "testuser1")
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, "list/job_detail.html")


class TestCustomerCreateView(CustomTestCase):
    def test_redirect_if_not_logged_in(self):
        response = self.client.post(reverse("list:add_customer"))
        self.assertRedirects(response, "/accounts/login/?next=/customer/add/")

    def test_view_uses_correct_template_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.post(reverse("list:add_customer"))

        self.assertEqual(str(response.context["user"]), "testuser1")
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, "list/add_customer.html")


class TestJobUpdateView(CustomTestCase):
    def test_redirect_if_not_logged_in(self):
        response = self.client.post(reverse("list:edit", kwargs={"pk": 1}))
        self.assertRedirects(response, "/accounts/login/?next=/job/edit/1/")

    def test_view_uses_correct_template_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.post(reverse("list:edit", kwargs={"pk": 1}))

        self.assertEqual(str(response.context["user"]), "testuser1")
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, "list/job_update_form.html")


class TestJobSortUpView(CustomTestCase):
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(
            reverse("list:sort_up", kwargs={"job_pk": 1, "machine_pk": 1})
        )
        self.assertRedirects(response, "/accounts/login/?next=/job/sort_up/1/1/")

    def test_redirect_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(
            reverse("list:sort_up", kwargs={"job_pk": 1, "machine_pk": 1})
        )

        self.assertRedirects(response, reverse("list:priority-list"))

    def test_sort_up(self):
        login = self.client.login(username="testuser1", password="testing123")

        test_job = MachineOrder.objects.get(
            machine=self.pin1, order=2, job__active=True
        ).job
        initial_order = test_job.order(machine=self.pin1)

        original_order_list = MachineOrder.objects.filter(
            machine=self.pin1, job__active=True
        ).order_by("order")

        self.client.get(
            reverse(
                "list:sort_up",
                kwargs={"job_pk": test_job.pk, "machine_pk": self.pin1.pk},
            )
        )

        test_job = Job.objects.get(pk=test_job.pk)

        self.assertNotEqual(initial_order, test_job.order(machine=self.pin1))
        self.assertEqual(initial_order - 1, test_job.order(machine=self.pin1))

        order_list = MachineOrder.objects.filter(
            machine=self.pin1, job__active=True
        ).order_by("order")

        self.assertNotEqual(order_list, original_order_list)

    def test_sort_up_after_machine_change(self):
        login = self.client.login(username="testuser1", password="testing123")

        test_job = MachineOrder.objects.get(
            machine=self.pin1, order=2, job__active=True
        ).job
        initial_order = test_job.order(machine=self.pin1)

        original_order_list = MachineOrder.objects.filter(
            machine=self.pin1, job__active=True
        )

        # pin2_job = (
        #     MachineOrder.objects.filter(machine=self.pin2, job__active=True).first().job
        # )
        destination_machine_initial_order = list(
            MachineOrder.objects.filter(machine=self.pin2, job__active=True)
        )

        test_job.change_machine(self.pin1, self.pin2)
        test_job = Job.objects.get(pk=test_job.pk)

        self.assertEqual(
            destination_machine_initial_order[-1].order + 1,
            test_job.order(machine=self.pin2),
        )

        self.client.get(
            reverse(
                "list:sort_up",
                kwargs={"job_pk": test_job.pk, "machine_pk": self.pin2.pk},
            )
        )
        test_job = Job.objects.get(pk=test_job.pk)

        self.assertEqual(
            destination_machine_initial_order[-1].order,
            test_job.order(machine=self.pin2),
        )

        order_list = MachineOrder.objects.filter(machine=self.pin2, job__active=True)

        self.assertNotEqual(original_order_list, order_list)


class TestJobSortDownView(CustomTestCase):
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(
            reverse("list:sort_down", kwargs={"job_pk": 1, "machine_pk": 1})
        )
        self.assertRedirects(response, "/accounts/login/?next=/job/sort_down/1/1/")

    def test_redirect_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(
            reverse("list:sort_down", kwargs={"job_pk": 1, "machine_pk": 1})
        )

        self.assertRedirects(response, reverse("list:priority-list"))

    def test_sort_down(self):
        login = self.client.login(username="testuser1", password="testing123")

        test_job = MachineOrder.objects.get(
            machine=self.pin1, order=1, job__active=True
        ).job
        initial_order = test_job.order(self.pin1)

        original_order_list = MachineOrder.objects.filter(
            machine=self.pin1, job__active=True
        ).order_by("order")

        self.client.get(
            reverse(
                "list:sort_down",
                kwargs={"job_pk": test_job.pk, "machine_pk": self.pin1.pk},
            )
        )

        test_job = Job.objects.get(pk=test_job.pk)

        self.assertNotEqual(initial_order, test_job.order(self.pin1))
        self.assertEqual(initial_order + 1, test_job.order(self.pin1))

        order_list = MachineOrder.objects.filter(
            machine=self.pin1, job__active=True
        ).order_by("order")

        self.assertNotEqual(original_order_list, order_list)


class TestJobToView(CustomTestCase):
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(
            reverse("list:job_to", kwargs={"job_pk": 1, "machine_pk": 1, "to": 1})
        )
        self.assertRedirects(response, "/accounts/login/?next=/job/to/1/1/1/")

    def test_redirect_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(
            reverse("list:job_to", kwargs={"job_pk": 1, "machine_pk": 1, "to": 1})
        )

        self.assertRedirects(response, reverse("list:priority-list"))

    def test_to_move_down(self):
        login = self.client.login(username="testuser1", password="testing123")

        test_job = MachineOrder.objects.get(
            machine=self.pin1, order=1, job__active=True
        ).job
        initial_order = test_job.order(self.pin1)

        original_order_list = MachineOrder.objects.filter(
            machine=self.pin1, job__active=True
        ).order_by("order")

        self.client.get(
            reverse(
                "list:job_to",
                kwargs={
                    "job_pk": test_job.pk,
                    "machine_pk": self.pin1.pk,
                    "to": initial_order + 1,
                },
            )
        )

        test_job = Job.objects.get(pk=test_job.pk)

        self.assertNotEqual(initial_order, test_job.order(self.pin1))
        self.assertEqual(initial_order + 1, test_job.order(self.pin1))

        order_list = MachineOrder.objects.filter(
            machine=self.pin1, job__active=True
        ).order_by("order")

        self.assertNotEqual(order_list, original_order_list)

    def test_to_move_up(self):
        login = self.client.login(username="testuser1", password="testing123")

        test_job = MachineOrder.objects.get(
            machine=self.pin1, order=2, job__active=True
        ).job
        initial_order = test_job.order(self.pin1)

        original_order_list = MachineOrder.objects.filter(
            machine=self.pin1, job__active=True
        ).order_by("order")

        self.client.get(
            reverse(
                "list:job_to",
                kwargs={
                    "job_pk": test_job.pk,
                    "machine_pk": self.pin1.pk,
                    "to": initial_order - 1,
                },
            )
        )

        test_job = Job.objects.get(pk=test_job.pk)

        self.assertNotEqual(initial_order, test_job.order(self.pin1))
        self.assertEqual(initial_order - 1, test_job.order(self.pin1))

        order_list = MachineOrder.objects.filter(
            machine=self.pin1, job__active=True
        ).order_by("order")

        self.assertNotEqual(order_list, original_order_list)


class TestJobArchiveView(CustomTestCase):
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("list:archive", kwargs={"pk": 1}))
        self.assertRedirects(response, "/accounts/login/?next=/job/archive/1/")

    def test_redirect_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(reverse("list:archive", kwargs={"pk": 1}))

        self.assertRedirects(response, reverse("list:priority-list"))


class TestProfileView(CustomTestCase):
    def test_redirect_if_not_logged_in(self):
        response = self.client.post(reverse("list:profile", kwargs={"pk": 1}))
        self.assertRedirects(response, "/accounts/login/?next=/profile/1/")

    def test_view_uses_correct_template_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(reverse("list:profile", kwargs={"pk": 1}))

        self.assertEqual(str(response.context["user"]), "testuser1")
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, "common/profile.html")


class TestProfileEditView(CustomTestCase):
    def test_redirect_if_not_logged_in(self):
        response = self.client.post(reverse("list:profile-edit", kwargs={"pk": 1}))
        self.assertRedirects(response, "/accounts/login/?next=/profile/edit/1/")

    def test_view_uses_correct_template_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(reverse("list:profile-edit", kwargs={"pk": 1}))

        self.assertEqual(str(response.context["user"]), "testuser1")
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, "common/profile_update.html")
