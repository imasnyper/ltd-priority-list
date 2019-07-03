from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from list.models import Machine, Customer, Profile, Job
from list.tests.util import create_jobs


class TestPriorityListView(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username='testuser1', password="testing123")

        self.pin1 = Machine.objects.create(name="Pinnacle 1")
        self.pin2 = Machine.objects.create(name="Pinnacle 2")
        self.starvision = Machine.objects.create(name="Starvision")

        self.p1 = Profile.objects.get(user=self.u1)
        self.p1.machines.set([self.pin1, self.pin2])
        self.p1.save()

        self.c1 = Customer.objects.create(name="Custy 1")
        self.c2 = Customer.objects.create(name="ABC Co.")

        # create referenced jobs for useing in testing
        create_jobs(3, self.pin1, [self.c1, self.c2])
        create_jobs(3, self.pin2, [self.c1, self.c2])
        create_jobs(3, self.starvision, [self.c1, self.c2])


    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("list:priority-list"))
        self.assertRedirects(response, '/accounts/login/?next=/')

    def test_view_uses_correct_template_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(reverse('list:priority-list'))

        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'list/index.html')

    def test_view_context(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(reverse('list:priority-list'))

        self.assertListEqual(list(response.context['machines']), list(self.p1.machines.all()))
        for machine in response.context['machines']:
            self.assertListEqual(list(machine.active_jobs()),
                                 list(Job.objects.filter(machine=machine,
                                                         active=True)))
        self.assertListEqual(list(response.context['customers']),
                             list(Customer.objects.all().order_by('name')))
        self.assertEqual(
            response.context['form']
                .get_initial_for_field(
                response.context['form'].fields['active'], 'active'
            ),
            True
        )


class TestArchiveView(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username='testuser1', password="testing123")

        self.pin1 = Machine.objects.create(name="Pinnacle 1")
        self.pin2 = Machine.objects.create(name="Pinnacle 2")
        self.starvision = Machine.objects.create(name="Starvision")

        self.c1 = Customer.objects.create(name="Custy 1")
        self.c2 = Customer.objects.create(name="ABC Co.")

        create_jobs(5, self.pin1, [self.c1, self.c2])
        create_jobs(5, self.pin2, [self.c1, self.c2])
        create_jobs(5, self.starvision, [self.c1, self.c2])

        jobs = Job.objects.all()
        for job in jobs:
            job.active = False
            job.save()

        profile = Profile.objects.get(user=self.u1)
        profile.machines.set([self.pin1, self.pin2, self.starvision])
        profile.save()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("list:archive-view"))
        self.assertRedirects(response, '/accounts/login/?next=/archive/')

    def test_view_uses_correct_template_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(reverse('list:archive-view'))

        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'list/archive.html')

    def test_pagination_is_ten(self):
        login = self.client.login(username="testuser1", password="testing123")

        response = self.client.get(reverse("list:archive-view"))
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue(len(response.context['jobs']) == 10)

    def test_lists_all_jobs(self):
        login = self.client.login(username='testuser1', password='testing123')

        response = self.client.get(reverse("list:archive-view") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue(len(response.context['jobs']) == 5)


class TestJobCreateView(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username='testuser1',
                                           password="testing123").save()

        self.pin1 = Machine.objects.create(name="Pinnacle 1")
        self.pin2 = Machine.objects.create(name="Pinnacle 2")
        self.starvision = Machine.objects.create(name="Starvision")

        self.c1 = Customer.objects.create(name="Custy 1")
        self.c2 = Customer.objects.create(name="ABC Co.")

        create_jobs(3, self.pin1, [self.c1, self.c2])
        create_jobs(3, self.pin2, [self.c1, self.c2])
        create_jobs(3, self.starvision, [self.c1, self.c2])

    def test_redirect_if_not_logged_in(self):
        response = self.client.post(reverse("list:add", kwargs={"machine_pk": 1}))
        self.assertRedirects(response, '/accounts/login/?next=/job/add/1/')

    def test_view_uses_correct_template_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.post(reverse('list:add', kwargs={"machine_pk": 1}))

        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'list/index.html')


class TestJobDetailView(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username='testuser1',
                                           password="testing123").save()

        self.pin1 = Machine.objects.create(name="Pinnacle 1")
        self.pin2 = Machine.objects.create(name="Pinnacle 2")
        self.starvision = Machine.objects.create(name="Starvision")

        self.c1 = Customer.objects.create(name="Custy 1")
        self.c2 = Customer.objects.create(name="ABC Co.")

        create_jobs(3, self.pin1, [self.c1, self.c2])
        create_jobs(3, self.pin2, [self.c1, self.c2])
        create_jobs(3, self.starvision, [self.c1, self.c2])

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("list:job-detail", kwargs={"pk": 1}))
        self.assertRedirects(response, '/accounts/login/?next=/job/1/')

    def test_view_uses_correct_template_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(reverse('list:job-detail', kwargs={"pk": 1}))

        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'list/job_detail.html')


class TestCustomerCreateView(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username='testuser1',
                                           password="testing123").save()

        self.pin1 = Machine.objects.create(name="Pinnacle 1")
        self.pin2 = Machine.objects.create(name="Pinnacle 2")
        self.starvision = Machine.objects.create(name="Starvision")

        self.c1 = Customer.objects.create(name="Custy 1")
        self.c2 = Customer.objects.create(name="ABC Co.")

        create_jobs(3, self.pin1, [self.c1, self.c2])
        create_jobs(3, self.pin2, [self.c1, self.c2])
        create_jobs(3, self.starvision, [self.c1, self.c2])

    def test_redirect_if_not_logged_in(self):
        response = self.client.post(reverse("list:add_customer"))
        self.assertRedirects(response, '/accounts/login/?next=/customer/add/')

    def test_view_uses_correct_template_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.post(reverse('list:add_customer'))

        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'list/add_customer.html')


class TestJobUpdateView(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username='testuser1',
                                           password="testing123").save()

        self.pin1 = Machine.objects.create(name="Pinnacle 1")
        self.pin2 = Machine.objects.create(name="Pinnacle 2")
        self.starvision = Machine.objects.create(name="Starvision")

        self.c1 = Customer.objects.create(name="Custy 1")
        self.c2 = Customer.objects.create(name="ABC Co.")

        create_jobs(3, self.pin1, [self.c1, self.c2])
        create_jobs(3, self.pin2, [self.c1, self.c2])
        create_jobs(3, self.starvision, [self.c1, self.c2])

    def test_redirect_if_not_logged_in(self):
        response = self.client.post(reverse("list:edit", kwargs={"pk": 1}))
        self.assertRedirects(response, '/accounts/login/?next=/job/edit/1/')

    def test_view_uses_correct_template_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.post(reverse('list:edit', kwargs={"pk": 1}))

        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'list/job_update_form.html')


class TestJobSortUpView(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username='testuser1',
                                           password="testing123").save()

        self.pin1 = Machine.objects.create(name="Pinnacle 1")
        self.pin2 = Machine.objects.create(name="Pinnacle 2")
        self.starvision = Machine.objects.create(name="Starvision")

        self.c1 = Customer.objects.create(name="Custy 1")
        self.c2 = Customer.objects.create(name="ABC Co.")

        create_jobs(3, self.pin1, [self.c1, self.c2])
        create_jobs(3, self.pin2, [self.c1, self.c2])
        create_jobs(3, self.starvision, [self.c1, self.c2])

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("list:sort_up", kwargs={"pk": 1}))
        self.assertRedirects(response, '/accounts/login/?next=/job/sort_up/1/')

    def test_redirect_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(reverse('list:sort_up', kwargs={"pk": 1}))

        self.assertRedirects(response, reverse("list:priority-list"))

    def test_sort_up(self):
        login = self.client.login(username="testuser1", password="testing123")

        test_job = Job.objects.get(machine=self.pin1, order=1, active=True)
        initial_order = test_job.order

        self.client.get(reverse('list:sort_up', kwargs={"pk": test_job.pk}))

        test_job = Job.objects.get(pk=test_job.pk)

        self.assertNotEqual(initial_order, test_job.order)
        self.assertEqual(initial_order - 1, test_job.order)

        order_list = [_.order for _ in test_job.get_ordering_queryset()]

        num_jobs = [_ for _ in
         range(Job.objects.filter(machine=self.pin1, active=True).count())]

        self.assertListEqual(order_list, num_jobs)

    def test_sort_up_after_machine_change(self):
        login = self.client.login(username="testuser1", password="testing123")

        test_job = Job.objects.get(machine=self.pin1, order=1, active=True)
        initial_order = test_job.order

        pin2_job = Job.objects.filter(machine=self.pin2).first()
        destination_machine_initial_order = list(pin2_job.get_ordering_queryset())

        test_job.machine = self.pin2
        test_job.save()

        self.assertEqual(destination_machine_initial_order[-1].order + 1, test_job.order)

        self.client.get(reverse('list:sort_up', kwargs={"pk": test_job.pk}))
        test_job = Job.objects.get(pk=test_job.pk)

        self.assertEqual(destination_machine_initial_order[-1].order, test_job.order)

        order_list = [_.order for _ in test_job.get_ordering_queryset()]

        num_jobs = [_ for _ in
         range(Job.objects.filter(machine=self.pin2, active=True).count())]

        self.assertListEqual(order_list, num_jobs)


class TestJobSortDownView(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username='testuser1',
                                           password="testing123").save()

        self.pin1 = Machine.objects.create(name="Pinnacle 1")
        self.pin2 = Machine.objects.create(name="Pinnacle 2")
        self.starvision = Machine.objects.create(name="Starvision")

        self.c1 = Customer.objects.create(name="Custy 1")
        self.c2 = Customer.objects.create(name="ABC Co.")

        create_jobs(3, self.pin1, [self.c1, self.c2])
        create_jobs(3, self.pin2, [self.c1, self.c2])
        create_jobs(3, self.starvision, [self.c1, self.c2])

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("list:sort_down", kwargs={"pk": 1}))
        self.assertRedirects(response, '/accounts/login/?next=/job/sort_down/1/')

    def test_redirect_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(reverse('list:sort_down', kwargs={"pk": 1}))

        self.assertRedirects(response, reverse("list:priority-list"))

    def test_sort_down(self):
        login = self.client.login(username="testuser1", password="testing123")

        test_job = Job.objects.get(machine=self.pin1, order=1, active=True)
        initial_order = test_job.order

        self.client.get(reverse('list:sort_down', kwargs={"pk": test_job.pk}))

        test_job = Job.objects.get(pk=test_job.pk)

        self.assertNotEqual(initial_order, test_job.order)
        self.assertEqual(initial_order + 1, test_job.order)

        order_list = [_.order for _ in test_job.get_ordering_queryset()]

        num_jobs = [_ for _ in range(Job.objects.filter(machine=self.pin1,
                                                        active=True).count())]

        self.assertListEqual(order_list, num_jobs)


class TestJobToView(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username='testuser1',
                                           password="testing123").save()

        self.pin1 = Machine.objects.create(name="Pinnacle 1")
        self.pin2 = Machine.objects.create(name="Pinnacle 2")
        self.starvision = Machine.objects.create(name="Starvision")

        self.c1 = Customer.objects.create(name="Custy 1")
        self.c2 = Customer.objects.create(name="ABC Co.")

        create_jobs(3, self.pin1, [self.c1, self.c2])
        create_jobs(3, self.pin2, [self.c1, self.c2])
        create_jobs(3, self.starvision, [self.c1, self.c2])

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("list:job_to", kwargs={"pk": 1,
                                                                  "to": 1}))
        self.assertRedirects(response,
                             '/accounts/login/?next=/job/to/1/1/')

    def test_redirect_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(reverse('list:job_to', kwargs={"pk": 1,
                                                                  "to": 1}))

        self.assertRedirects(response, reverse("list:priority-list"))

    def test_to_move_down(self):
        login = self.client.login(username="testuser1", password="testing123")

        test_job = Job.objects.get(machine=self.pin1, order=1, active=True)
        initial_order = test_job.order

        self.client.get(reverse('list:job_to', kwargs={"pk": test_job.pk,
                                                       "to": initial_order + 1}))

        test_job = Job.objects.get(pk=test_job.pk)

        self.assertNotEqual(initial_order, test_job.order)
        self.assertEqual(initial_order + 1, test_job.order)

        order_list = [_.order for _ in test_job.get_ordering_queryset()]

        num_jobs = [_ for _ in range(Job.objects.filter(machine=self.pin1,
                                                        active=True).count())]

        self.assertListEqual(order_list, num_jobs)

    def test_to_move_up(self):
        login = self.client.login(username="testuser1", password="testing123")

        test_job = Job.objects.get(machine=self.pin1, order=2, active=True)
        initial_order = test_job.order

        self.client.get(reverse('list:job_to', kwargs={"pk": test_job.pk,
                                                       "to": initial_order - 1}))

        test_job = Job.objects.get(pk=test_job.pk)

        self.assertNotEqual(initial_order, test_job.order)
        self.assertEqual(initial_order - 1, test_job.order)

        order_list = [_.order for _ in test_job.get_ordering_queryset()]

        num_jobs = [_ for _ in range(Job.objects.filter(machine=self.pin1,
                                                        active=True).count())]

        self.assertListEqual(order_list, num_jobs)



class TestJobArchiveView(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username='testuser1',
                                           password="testing123").save()

        self.pin1 = Machine.objects.create(name="Pinnacle 1")
        self.pin2 = Machine.objects.create(name="Pinnacle 2")
        self.starvision = Machine.objects.create(name="Starvision")

        self.c1 = Customer.objects.create(name="Custy 1")
        self.c2 = Customer.objects.create(name="ABC Co.")

        create_jobs(3, self.pin1, [self.c1, self.c2])
        create_jobs(3, self.pin2, [self.c1, self.c2])
        create_jobs(3, self.starvision, [self.c1, self.c2])

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("list:archive", kwargs={"pk": 1}))
        self.assertRedirects(response, '/accounts/login/?next=/job/archive/1/')

    def test_redirect_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(reverse('list:archive', kwargs={"pk": 1}))

        self.assertRedirects(response, reverse("list:priority-list"))


class TestProfileView(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username='testuser1',
                                           password="testing123").save()

        self.pin1 = Machine.objects.create(name="Pinnacle 1")
        self.pin2 = Machine.objects.create(name="Pinnacle 2")
        self.starvision = Machine.objects.create(name="Starvision")

        self.c1 = Customer.objects.create(name="Custy 1")
        self.c2 = Customer.objects.create(name="ABC Co.")

        create_jobs(3, self.pin1, [self.c1, self.c2])
        create_jobs(3, self.pin2, [self.c1, self.c2])
        create_jobs(3, self.starvision, [self.c1, self.c2])

    def test_redirect_if_not_logged_in(self):
        response = self.client.post(reverse("list:profile", kwargs={"pk": 1}))
        self.assertRedirects(response, '/accounts/login/?next=/profile/1/')

    def test_view_uses_correct_template_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(reverse('list:profile', kwargs={"pk": 1}))

        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'common/profile.html')


class TestProfileEditView(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username='testuser1',
                                           password="testing123").save()

        self.pin1 = Machine.objects.create(name="Pinnacle 1")
        self.pin2 = Machine.objects.create(name="Pinnacle 2")
        self.starvision = Machine.objects.create(name="Starvision")

        self.c1 = Customer.objects.create(name="Custy 1")
        self.c2 = Customer.objects.create(name="ABC Co.")

        create_jobs(3, self.pin1, [self.c1, self.c2])
        create_jobs(3, self.pin2, [self.c1, self.c2])
        create_jobs(3, self.starvision, [self.c1, self.c2])

    def test_redirect_if_not_logged_in(self):
        response = self.client.post(reverse("list:profile-edit", kwargs={"pk": 1}))
        self.assertRedirects(response, '/accounts/login/?next=/profile/edit/1/')

    def test_view_uses_correct_template_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(reverse('list:profile-edit', kwargs={"pk": 1}))

        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'common/profile_update.html')
