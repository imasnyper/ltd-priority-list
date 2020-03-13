import random
from datetime import datetime

from django.urls import reverse
from django.utils.timezone import make_aware
from rest_framework import status
from rest_framework.exceptions import ValidationError

from list.models import Customer, Profile, Job, MachineOrder, Detail, Machine
from . import ViewTestCase, CustomAPITestCase


class TestPriorityListView(ViewTestCase):
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


class TestArchiveView(ViewTestCase):
    def setUp(self):
        super().setUp()
        jobs = Job.objects.all()
        for job in jobs:
            job.active = False
            job.save()

        profile = Profile.objects.get(user=self.u1)
        profile.machines.set([self.m1, self.m2, self.m3])
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


class TestJobCreateView(ViewTestCase):
    def test_redirect_if_not_logged_in(self):
        response = self.client.post(reverse("list:add", kwargs={"machine_pk": 1}))
        self.assertRedirects(response, "/accounts/login/?next=/job/add/1/")

    def test_view_uses_correct_template_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.post(reverse("list:add", kwargs={"machine_pk": 1}))

        self.assertEqual(str(response.context["user"]), "testuser1")
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, "list/index.html")

    def test_form_valid(self):
        login = self.client.login(username="testuser1", password="testing123")
        customer = self.c1.pk
        job = 6789
        data = {"job_number": job, "customer": customer}

        response = self.client.post(
            reverse("list:add", kwargs={"machine_pk": 1}), data=data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Job.objects.last().job_number, 6789)


class TestJobDetailView(ViewTestCase):
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


class TestJobOverviewView(ViewTestCase):
    def test_context_data(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(
            reverse("list:job-overview", kwargs={"pk": self.j1.pk})
        )

        self.assertEqual(response.context_data["job"], self.j1)
        self.assertListEqual(
            list(response.context_data["details"]),
            list(Detail.objects.filter(job=self.j1).order_by("machine__name")),
        )
        self.assertListEqual(
            list(response.context_data["machines"]),
            list(
                Machine.objects.filter(details__in=Detail.objects.filter(job=self.j1))
            ),
        )


class TestDetailViewSet(CustomAPITestCase):
    def test_create_detail_with_authentication(self):
        token = self.client.post(
            reverse("authenticate"),
            {"username": "testuser1", "password": "testing123"},
            format="json",
        ).data.get("token", None)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        url = reverse("api:details-list")
        data = {
            "job": {"job_number": 1234, "customer": {"name": "ABC co."}},
            "machine": {"name": "Pinnacle 1"},
            "quantity": 1,
            "ltd_item_number": 1,
            "outsource_detail_number": "10",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Job.objects.count(), 3
        )  # 2 jobs are created in the class's setup method
        self.assertEqual(Detail.objects.count(), 1)
        self.assertEqual(Detail.objects.get().job.job_number, 1234)

    def test_create_detail_not_authenticated(self):
        url = reverse("api:details-list")
        data = {
            "job": {"job_number": 1234, "customer": {"name": "ABC co."}},
            "machine": {"name": "Pinnacle 1"},
            "quantity": 1,
            "ltd_item_number": 1,
            "outsource_detail_number": "10",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.data.get("detail", None),
            "Authentication credentials were not provided.",
        )

    def test_create_detail_no_customer_job_doesnt_exist(self):
        url = reverse("api:details-list")
        data = {
            "job": {"job_number": 1234},
            "machine": {"name": "Pinnacle 1"},
            "quantity": 1,
            "ltd_item_number": 1,
            "outsource_detail_number": "10",
        }
        self.client.force_authenticate(user=self.u1)
        response = self.client.post(url, data, "json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data[0], "Customer may not be blank if job doesn't exist."
        )

    def test_create_detail_lowercase_machine_name(self):
        url = reverse("api:details-list")
        data = {
            "job": {"job_number": 1234, "customer": {"name": "ABC co."}},
            "machine": {"name": "pinnacle 1"},
            "quantity": 1,
            "ltd_item_number": 2,
            "outsource_detail_number": "20",
        }
        self.client.force_authenticate(user=self.u1)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Job.objects.count(), 3
        )  # 2 jobs are created in the class's setup method
        self.assertEqual(Detail.objects.count(), 1)
        self.assertEqual(Detail.objects.get().job.job_number, 1234)
        self.assertEqual(Detail.objects.get().machine, self.m1)

    def test_create_detail_uppercase_customer_name(self):
        url = reverse("api:details-list")
        data = {
            "job": {"job_number": 1111, "customer": {"name": "C1"}},
            "machine": {"name": "pinnacle 1"},
            "quantity": 1,
            "ltd_item_number": 2,
            "outsource_detail_number": "20",
        }
        self.client.force_authenticate(user=self.u1)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Job.objects.count(), 2
        )  # 2 jobs are created in the class's setup method
        self.assertEqual(Detail.objects.count(), 1)
        self.assertEqual(Detail.objects.get().job.job_number, 1111)
        self.assertEqual(Detail.objects.get().machine, self.m1)


class TestCustomerCreateView(ViewTestCase):
    def test_redirect_if_not_logged_in(self):
        response = self.client.post(reverse("list:add_customer"))
        self.assertRedirects(response, "/accounts/login/?next=/customer/add/")

    def test_view_uses_correct_template_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.post(reverse("list:add_customer"))

        self.assertEqual(str(response.context["user"]), "testuser1")
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, "list/add_customer.html")


class TestJobUpdateView(ViewTestCase):
    def test_redirect_if_not_logged_in(self):
        response = self.client.post(reverse("list:edit", kwargs={"pk": 1}))
        self.assertRedirects(response, "/accounts/login/?next=/job/edit/1/")

    def test_view_uses_correct_template_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.post(reverse("list:edit", kwargs={"pk": 1}))

        self.assertEqual(str(response.context["user"]), "testuser1")
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, "list/job_update_form.html")


class TestJobSortUpView(ViewTestCase):
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
            machine=self.m1, order=2, job__active=True
        ).job
        initial_order = test_job.order(machine=self.m1)

        original_order_list = MachineOrder.objects.filter(
            machine=self.m1, job__active=True
        ).order_by("order")

        self.client.get(
            reverse(
                "list:sort_up",
                kwargs={"job_pk": test_job.pk, "machine_pk": self.m1.pk},
            )
        )

        test_job = Job.objects.get(pk=test_job.pk)

        self.assertNotEqual(initial_order, test_job.order(machine=self.m1))
        self.assertEqual(initial_order - 1, test_job.order(machine=self.m1))

        order_list = MachineOrder.objects.filter(
            machine=self.m1, job__active=True
        ).order_by("order")

        self.assertNotEqual(order_list, original_order_list)

    def test_sort_up_after_machine_change(self):
        login = self.client.login(username="testuser1", password="testing123")

        test_job = MachineOrder.objects.get(
            machine=self.m1, order=2, job__active=True
        ).job
        initial_order = test_job.order(machine=self.m1)

        original_order_list = MachineOrder.objects.filter(
            machine=self.m1, job__active=True
        )

        # pin2_job = (
        #     MachineOrder.objects.filter(machine=self.pin2, job__active=True).first().job
        # )
        destination_machine_initial_order = list(
            MachineOrder.objects.filter(machine=self.m2, job__active=True)
        )

        test_job.change_machine(self.m1, self.m2)
        test_job = Job.objects.get(pk=test_job.pk)

        self.assertEqual(
            destination_machine_initial_order[-1].order + 1,
            test_job.order(machine=self.m2),
        )

        self.client.get(
            reverse(
                "list:sort_up",
                kwargs={"job_pk": test_job.pk, "machine_pk": self.m2.pk},
            )
        )
        test_job = Job.objects.get(pk=test_job.pk)

        self.assertEqual(
            destination_machine_initial_order[-1].order,
            test_job.order(machine=self.m2),
        )

        order_list = MachineOrder.objects.filter(machine=self.m2, job__active=True)

        self.assertNotEqual(original_order_list, order_list)


class TestJobSortDownView(ViewTestCase):
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
            machine=self.m1, order=1, job__active=True
        ).job
        initial_order = test_job.order(self.m1)

        original_order_list = MachineOrder.objects.filter(
            machine=self.m1, job__active=True
        ).order_by("order")

        self.client.get(
            reverse(
                "list:sort_down",
                kwargs={"job_pk": test_job.pk, "machine_pk": self.m1.pk},
            )
        )

        test_job = Job.objects.get(pk=test_job.pk)

        self.assertNotEqual(initial_order, test_job.order(self.m1))
        self.assertEqual(initial_order + 1, test_job.order(self.m1))

        order_list = MachineOrder.objects.filter(
            machine=self.m1, job__active=True
        ).order_by("order")

        self.assertNotEqual(original_order_list, order_list)


class TestJobToView(ViewTestCase):
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
            machine=self.m1, order=1, job__active=True
        ).job
        initial_order = test_job.order(self.m1)

        original_order_list = MachineOrder.objects.filter(
            machine=self.m1, job__active=True
        ).order_by("order")

        self.client.get(
            reverse(
                "list:job_to",
                kwargs={
                    "job_pk": test_job.pk,
                    "machine_pk": self.m1.pk,
                    "to": initial_order + 1,
                },
            )
        )

        test_job = Job.objects.get(pk=test_job.pk)

        self.assertNotEqual(initial_order, test_job.order(self.m1))
        self.assertEqual(initial_order + 1, test_job.order(self.m1))

        order_list = MachineOrder.objects.filter(
            machine=self.m1, job__active=True
        ).order_by("order")

        self.assertNotEqual(order_list, original_order_list)

    def test_to_move_up(self):
        login = self.client.login(username="testuser1", password="testing123")

        test_job = MachineOrder.objects.get(
            machine=self.m1, order=2, job__active=True
        ).job
        initial_order = test_job.order(self.m1)

        original_order_list = MachineOrder.objects.filter(
            machine=self.m1, job__active=True
        ).order_by("order")

        self.client.get(
            reverse(
                "list:job_to",
                kwargs={
                    "job_pk": test_job.pk,
                    "machine_pk": self.m1.pk,
                    "to": initial_order - 1,
                },
            )
        )

        test_job = Job.objects.get(pk=test_job.pk)

        self.assertNotEqual(initial_order, test_job.order(self.m1))
        self.assertEqual(initial_order - 1, test_job.order(self.m1))

        order_list = MachineOrder.objects.filter(
            machine=self.m1, job__active=True
        ).order_by("order")

        self.assertNotEqual(order_list, original_order_list)


class TestJobSearchView(ViewTestCase):
    def setUp(self):
        super().setUp()
        self.dates = [
            datetime(2019, 10, 1),
            datetime(2019, 11, 1),
            datetime(2019, 12, 1),
        ]
        for i, d in enumerate(self.dates):
            self.dates[i] = make_aware(d)
        jobs = list(Job.objects.all())
        jobs.pop(0)
        jobs.pop(0)

        # set up jobs to test date_added
        for i, _ in enumerate(range(3)):
            job = random.choice(jobs)
            setattr(self, "j" + str(i + 3), job)
            jobs.remove(job)
            job.date_added = self.dates[i]
            job.save()

        # set up jobs to test due_date
        for i, _ in enumerate(range(3)):
            job = random.choice(jobs)
            setattr(self, "j" + str(i + 6), job)
            jobs.remove(job)
            job.due_date = self.dates[i]
            job.save()

        # set up jobs to test datetime_completed
        for i, _ in enumerate(range(3)):
            job = random.choice(jobs)
            setattr(self, "j" + str(i + 9), job)
            jobs.remove(job)
            job.datetime_completed = self.dates[i]
            job.save()

        self.j12 = jobs.pop()
        self.j12.description = "This is my description"
        self.j12.save()

    def test_invalid_form(self):
        login = self.client.login(username="testuser1", password="testing123")

        data = {"job_number": "something that should fail"}
        link = reverse("list:search")

        self.assertRaises(ValidationError, self.client.get, link, data)

    def test_empty_form(self):
        login = self.client.login(username="testuser1", password="testing123")

        data = {}
        link = reverse("list:search")

        response = self.client.get(link, data)
        self.assertListEqual(list(response.context_data["jobs"]), [])

    def test_context_data(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(
            reverse("list:search"), data={"job_number": 1111, "customer": self.c1.pk}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context_data["jobs"]),
            list(Job.objects.filter(job_number=1111)),
        )
        self.assertEqual(
            response.context_data["search_terms"],
            {"job_number": "1111", "customer": str(self.c1.pk)},
        )
        self.assertEqual(response.context_data["args"], "&job_number=1111&customer=1")

    def test_date_added_lte(self):
        login = self.client.login(username="testuser1", password="testing123")

        data = {"date_added": self.dates[2].date(), "date_added_lte": "on"}
        response = self.client.get(reverse("list:search"), data=data)
        self.assertListEqual(
            list(response.context_data["jobs"]), [self.j3, self.j4, self.j5]
        )

    def test_date_added_gte(self):
        login = self.client.login(username="testuser1", password="testing123")

        data = {"date_added": self.dates[0].date(), "date_added_gte": "on"}
        response = self.client.get(reverse("list:search"), data=data)
        compare_jobs = Job.objects.filter(date_added__gte=self.dates[0]).order_by(
            "date_added"
        )[:5]
        self.assertListEqual(list(response.context_data["jobs"]), list(compare_jobs))

    def test_date_added(self):
        login = self.client.login(username="testuser1", password="testing123")

        data = {"date_added": self.dates[0].date()}
        response = self.client.get(reverse("list:search"), data=data)
        compare_job = list(Job.objects.filter(date_added=self.dates[0]))
        self.assertListEqual(list(response.context_data["jobs"]), compare_job)

    def test_due_date_lte(self):
        login = self.client.login(username="testuser1", password="testing123")

        data = {"due_date": self.dates[2].date(), "due_date_lte": "on"}
        response = self.client.get(reverse("list:search"), data=data)
        response_list = list(response.context_data["jobs"])
        response_list = sorted(response_list, key=lambda x: x.due_date)
        check_list = sorted([self.j6, self.j7, self.j8], key=lambda x: x.due_date)
        self.assertListEqual(list(response_list), check_list)

    def test_due_date_gte(self):
        login = self.client.login(username="testuser1", password="testing123")

        data = {"due_date": self.dates[0].date(), "due_date_gte": "on"}
        response = self.client.get(reverse("list:search"), data=data)
        compare_jobs = Job.objects.filter(due_date__gte=self.dates[0]).order_by(
            "date_added"
        )[:5]
        self.assertListEqual(list(response.context_data["jobs"]), list(compare_jobs))

    def test_due_date_added(self):
        login = self.client.login(username="testuser1", password="testing123")

        data = {"due_date": self.dates[0].date()}
        response = self.client.get(reverse("list:search"), data=data)
        compare_job = list(Job.objects.filter(due_date=self.dates[0]))
        self.assertListEqual(list(response.context_data["jobs"]), compare_job)

    def test_description(self):
        login = self.client.login(username="testuser1", password="testing123")

        data = {"description": "This is my description"}
        response = self.client.get(reverse("list:search"), data=data)
        compare_job = self.j12
        self.assertEqual(response.context_data["jobs"][0], compare_job)

    def test_datetime_completed_lte(self):
        login = self.client.login(username="testuser1", password="testing123")

        data = {
            "datetime_completed": self.dates[0].date(),
            "datetime_completed_lte": "on",
        }
        response = self.client.get(reverse("list:search"), data=data)
        compare_jobs = list(Job.objects.filter(datetime_completed__lte=self.dates[0]))
        self.assertListEqual(list(response.context_data["jobs"]), compare_jobs)

    def test_datetime_completed_gte(self):
        login = self.client.login(username="testuser1", password="testing123")

        data = {
            "datetime_completed": self.dates[2].date(),
            "datetime_completed_gte": "on",
        }
        response = self.client.get(reverse("list:search"), data=data)
        compare_jobs = list(Job.objects.filter(datetime_completed__gte=self.dates[2]))
        self.assertListEqual(list(response.context_data["jobs"]), compare_jobs)

    def test_datetime_completed(self):
        login = self.client.login(username="testuser1", password="testing123")

        data = {
            "datetime_completed": self.dates[2].date(),
        }
        response = self.client.get(reverse("list:search"), data=data)
        compare_jobs = list(Job.objects.filter(datetime_completed=self.dates[2]))
        self.assertListEqual(list(response.context_data["jobs"]), compare_jobs)


class TestJobArchiveView(ViewTestCase):
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("list:archive", kwargs={"pk": 1}))
        self.assertRedirects(response, "/accounts/login/?next=/job/archive/1/")

    def test_redirect_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(reverse("list:archive", kwargs={"pk": 1}))

        self.assertRedirects(response, reverse("list:priority-list"))


class TestProfileView(ViewTestCase):
    def test_redirect_if_not_logged_in(self):
        response = self.client.post(reverse("list:profile", kwargs={"pk": 1}))
        self.assertRedirects(response, "/accounts/login/?next=/profile/1/")

    def test_view_uses_correct_template_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(reverse("list:profile", kwargs={"pk": 1}))

        self.assertEqual(str(response.context["user"]), "testuser1")
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, "common/profile.html")


class TestProfileEditView(ViewTestCase):
    def test_redirect_if_not_logged_in(self):
        response = self.client.post(reverse("list:profile-edit", kwargs={"pk": 1}))
        self.assertRedirects(response, "/accounts/login/?next=/profile/edit/1/")

    def test_view_uses_correct_template_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(reverse("list:profile-edit", kwargs={"pk": 1}))

        self.assertEqual(str(response.context["user"]), "testuser1")
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, "common/profile_update.html")
