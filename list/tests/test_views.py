from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from list.models import Machine, Customer, Profile
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

        self.j1 = create_jobs(3, self.pin1, [self.c1, self.c2])
        self.j2 = create_jobs(3, self.pin2, [self.c1, self.c2])
        self.j3 = create_jobs(3, self.starvision, [self.c1, self.c2])

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
        # for machine in response.context['machines']:
            # self.assertEqual(list(response.context['']))
        self.assertListEqual(list(response.context['customers']), list(Customer.objects.all().order_by('name')))
        self.assertEqual(
            response.context['form']
                .get_initial_for_field(
                response.context['form'].fields['active'], 'active'
            ),
            True
        )


class TestArchiveView(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username='testuser1', password="testing123").save()

        self.pin1 = Machine.objects.create(name="Pinnacle 1")
        self.pin2 = Machine.objects.create(name="Pinnacle 2")
        self.starvision = Machine.objects.create(name="Starvision")

        self.c1 = Customer.objects.create(name="Custy 1")
        self.c2 = Customer.objects.create(name="ABC Co.")

        self.j1 = create_jobs(3, self.pin1, [self.c1, self.c2])
        self.j2 = create_jobs(3, self.pin2, [self.c1, self.c2])
        self.j3 = create_jobs(3, self.starvision, [self.c1, self.c2])

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("list:archive-view"))
        self.assertRedirects(response, '/accounts/login/?next=/archive/')

    def test_view_uses_correct_template_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(reverse('list:archive-view'))

        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'list/archive.html')


class TestJobCreateView(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username='testuser1', password="testing123").save()

        self.pin1 = Machine.objects.create(name="Pinnacle 1")
        self.pin2 = Machine.objects.create(name="Pinnacle 2")
        self.starvision = Machine.objects.create(name="Starvision")

        self.c1 = Customer.objects.create(name="Custy 1")
        self.c2 = Customer.objects.create(name="ABC Co.")

        self.j1 = create_jobs(3, self.pin1, [self.c1, self.c2])
        self.j2 = create_jobs(3, self.pin2, [self.c1, self.c2])
        self.j3 = create_jobs(3, self.starvision, [self.c1, self.c2])

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
        self.u1 = User.objects.create_user(username='testuser1', password="testing123").save()

        self.pin1 = Machine.objects.create(name="Pinnacle 1")
        self.pin2 = Machine.objects.create(name="Pinnacle 2")
        self.starvision = Machine.objects.create(name="Starvision")

        self.c1 = Customer.objects.create(name="Custy 1")
        self.c2 = Customer.objects.create(name="ABC Co.")

        self.j1 = create_jobs(3, self.pin1, [self.c1, self.c2])
        self.j2 = create_jobs(3, self.pin2, [self.c1, self.c2])
        self.j3 = create_jobs(3, self.starvision, [self.c1, self.c2])

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
        self.u1 = User.objects.create_user(username='testuser1', password="testing123").save()

        self.pin1 = Machine.objects.create(name="Pinnacle 1")
        self.pin2 = Machine.objects.create(name="Pinnacle 2")
        self.starvision = Machine.objects.create(name="Starvision")

        self.c1 = Customer.objects.create(name="Custy 1")
        self.c2 = Customer.objects.create(name="ABC Co.")

        self.j1 = create_jobs(3, self.pin1, [self.c1, self.c2])
        self.j2 = create_jobs(3, self.pin2, [self.c1, self.c2])
        self.j3 = create_jobs(3, self.starvision, [self.c1, self.c2])

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
        self.u1 = User.objects.create_user(username='testuser1', password="testing123").save()

        self.pin1 = Machine.objects.create(name="Pinnacle 1")
        self.pin2 = Machine.objects.create(name="Pinnacle 2")
        self.starvision = Machine.objects.create(name="Starvision")

        self.c1 = Customer.objects.create(name="Custy 1")
        self.c2 = Customer.objects.create(name="ABC Co.")

        self.j1 = create_jobs(3, self.pin1, [self.c1, self.c2])
        self.j2 = create_jobs(3, self.pin2, [self.c1, self.c2])
        self.j3 = create_jobs(3, self.starvision, [self.c1, self.c2])

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
        self.u1 = User.objects.create_user(username='testuser1', password="testing123").save()

        self.pin1 = Machine.objects.create(name="Pinnacle 1")
        self.pin2 = Machine.objects.create(name="Pinnacle 2")
        self.starvision = Machine.objects.create(name="Starvision")

        self.c1 = Customer.objects.create(name="Custy 1")
        self.c2 = Customer.objects.create(name="ABC Co.")

        self.j1 = create_jobs(3, self.pin1, [self.c1, self.c2])
        self.j2 = create_jobs(3, self.pin2, [self.c1, self.c2])
        self.j3 = create_jobs(3, self.starvision, [self.c1, self.c2])

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("list:sort_up", kwargs={"pk": 1}))
        self.assertRedirects(response, '/accounts/login/?next=/job/sort_up/1/')

    def test_redirect_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(reverse('list:sort_up', kwargs={"pk": 1}))

        self.assertRedirects(response, reverse("list:priority-list"))


class TestJobSortDownView(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username='testuser1', password="testing123").save()

        self.pin1 = Machine.objects.create(name="Pinnacle 1")
        self.pin2 = Machine.objects.create(name="Pinnacle 2")
        self.starvision = Machine.objects.create(name="Starvision")

        self.c1 = Customer.objects.create(name="Custy 1")
        self.c2 = Customer.objects.create(name="ABC Co.")

        self.j1 = create_jobs(3, self.pin1, [self.c1, self.c2])
        self.j2 = create_jobs(3, self.pin2, [self.c1, self.c2])
        self.j3 = create_jobs(3, self.starvision, [self.c1, self.c2])

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("list:sort_down", kwargs={"pk": 1}))
        self.assertRedirects(response, '/accounts/login/?next=/job/sort_down/1/')

    def test_redirect_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(reverse('list:sort_down', kwargs={"pk": 1}))

        self.assertRedirects(response, reverse("list:priority-list"))


class TestJobArchiveView(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username='testuser1', password="testing123").save()

        self.pin1 = Machine.objects.create(name="Pinnacle 1")
        self.pin2 = Machine.objects.create(name="Pinnacle 2")
        self.starvision = Machine.objects.create(name="Starvision")

        self.c1 = Customer.objects.create(name="Custy 1")
        self.c2 = Customer.objects.create(name="ABC Co.")

        self.j1 = create_jobs(3, self.pin1, [self.c1, self.c2])
        self.j2 = create_jobs(3, self.pin2, [self.c1, self.c2])
        self.j3 = create_jobs(3, self.starvision, [self.c1, self.c2])

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("list:archive", kwargs={"pk": 1}))
        self.assertRedirects(response, '/accounts/login/?next=/job/archive/1/')

    def test_redirect_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(reverse('list:archive', kwargs={"pk": 1}))

        self.assertRedirects(response, reverse("list:priority-list"))


class TestProfileView(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username='testuser1', password="testing123").save()

        self.pin1 = Machine.objects.create(name="Pinnacle 1")
        self.pin2 = Machine.objects.create(name="Pinnacle 2")
        self.starvision = Machine.objects.create(name="Starvision")

        self.c1 = Customer.objects.create(name="Custy 1")
        self.c2 = Customer.objects.create(name="ABC Co.")

        self.j1 = create_jobs(3, self.pin1, [self.c1, self.c2])
        self.j2 = create_jobs(3, self.pin2, [self.c1, self.c2])
        self.j3 = create_jobs(3, self.starvision, [self.c1, self.c2])

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
        self.u1 = User.objects.create_user(username='testuser1', password="testing123").save()

        self.pin1 = Machine.objects.create(name="Pinnacle 1")
        self.pin2 = Machine.objects.create(name="Pinnacle 2")
        self.starvision = Machine.objects.create(name="Starvision")

        self.c1 = Customer.objects.create(name="Custy 1")
        self.c2 = Customer.objects.create(name="ABC Co.")

        self.j1 = create_jobs(3, self.pin1, [self.c1, self.c2])
        self.j2 = create_jobs(3, self.pin2, [self.c1, self.c2])
        self.j3 = create_jobs(3, self.starvision, [self.c1, self.c2])

    def test_redirect_if_not_logged_in(self):
        response = self.client.post(reverse("list:profile-edit", kwargs={"pk": 1}))
        self.assertRedirects(response, '/accounts/login/?next=/profile/edit/1/')

    def test_view_uses_correct_template_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(reverse('list:profile-edit', kwargs={"pk": 1}))

        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'common/profile_update.html')
