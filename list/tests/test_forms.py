from list.forms import CustomerForm
from list.tests import BaseTestCase


class TestCustomerForm(BaseTestCase):
    def test_clean_name_name_doesnt_exist(self):
        data = {"name": "test customer name"}
        form = CustomerForm(data=data)

        self.assertTrue(form.is_valid())

    def test_clean_name_name_exists(self):
        data = {"name": "C1"}
        form = CustomerForm(data=data)

        self.assertFalse(form.is_valid())
