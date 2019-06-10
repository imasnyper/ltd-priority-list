from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from list.models import Machine, Customer
from list.tests.util import create_jobs


class TestPriorityListView(TestCase):
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
        response = self.client.get(reverse("list:priority-list"))
        self.assertRedirects(response, '/accounts/login/?next=/')

    def test_view_uses_correct_template_if_logged_in(self):
        login = self.client.login(username="testuser1", password="testing123")
        response = self.client.get(reverse('list:priority-list'))

        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'list/index.html')