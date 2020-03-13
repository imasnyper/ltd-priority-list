from rest_framework.serializers import ValidationError

from list.models import Job, Customer
from . import CustomAPITestCase
from ..serializers import DetailSerializer


# noinspection PyTypeChecker
class TestDetailSerializer(CustomAPITestCase):
    def test_machine_validator_machine_doesnt_exist(self):
        data = {
            "job": {"job_number": 1111, "customer": {"name": "c1"}},
            "machine": {"name": "doesnt exist"},
            "quantity": 1,
            "ltd_item_number": 1,
            "outsource_detail_number": "10",
        }
        detail_serializer = DetailSerializer(data=data)

        self.assertRaises(
            ValidationError, detail_serializer.is_valid, ["raise_exception", "true"]
        )

    def test_machine_validator_machine_blank(self):
        data = {
            "job": {"job_number": 1111, "customer": {"name": "c1"}},
            "quantity": 1,
            "ltd_item_number": 1,
            "outsource_detail_number": "10",
        }
        detail_serializer = DetailSerializer(data=data)
        detail_serializer.is_valid()

        self.assertEqual(detail_serializer.validated_data["job"]["job_number"], 1111)
        self.assertEqual(
            detail_serializer.validated_data["job"].get("machine", None), None
        )

    def test_job_serializer_existing_job(self):
        data = {
            "job": {"job_number": 1111, "customer": {"name": "c1"}},
            "machine": {"name": "Pinnacle 1"},
            "quantity": 1,
            "ltd_item_number": 1,
            "outsource_detail_number": "10",
        }
        detail_serializer: DetailSerializer = DetailSerializer(data=data)
        detail_serializer.is_valid()
        d = detail_serializer.save()

        self.assertEqual(d.job.job_number, 1111)
        self.assertEqual(d.job.customer, self.c1)

    def test_job_serializer_new_job(self):
        data = {
            "job": {"job_number": 3333, "customer": {"name": "c1"}},
            "machine": {"name": "Pinnacle 1"},
            "quantity": 1,
            "ltd_item_number": 1,
            "outsource_detail_number": "10",
        }
        detail_serializer: DetailSerializer = DetailSerializer(data=data)
        detail_serializer.is_valid()
        d = detail_serializer.save()

        self.assertEqual(d.job.job_number, 3333)
        self.assertEqual(d.job.customer, self.c1)

    def test_job_validator_job_number_low(self):
        data = {
            "job": {"job_number": 999, "customer": {"name": "test"}},
            "machine": {"name": "Pinnacle 1"},
            "quantity": 1,
            "ltd_item_number": 1,
            "outsource_detail_number": "10",
        }
        detail_serializer: DetailSerializer = DetailSerializer(data=data)

        self.assertRaises(
            ValidationError, detail_serializer.is_valid, ["raise_exception", "true"]
        )

    def test_job_validator_job_number_high(self):
        data = {
            "job": {"job_number": 99999, "customer": {"name": "test"}},
            "machine": {"name": "Pinnacle 1"},
            "quantity": 1,
            "ltd_item_number": 1,
            "outsource_detail_number": "10",
        }
        detail_serializer: DetailSerializer = DetailSerializer(data=data)

        self.assertRaises(
            ValidationError, detail_serializer.is_valid, ["raise_exception", "true"]
        )

    def test_machine_validator_job_and_machine_exists(self):
        # create job first for serializer validation
        customer = Customer.objects.create(name="test")
        job = Job.objects.create(job_number=4444, customer=customer)

        data = {
            "job": {"job_number": 4444, "customer": {"name": "test"}},
            "machine": {"name": "Pinnacle 1"},
            "quantity": 1,
            "ltd_item_number": 1,
            "outsource_detail_number": "10",
        }
        detail_serializer = DetailSerializer(data=data)
        detail_serializer.is_valid()

        self.assertIsNotNone(detail_serializer.validated_data)
        self.assertEqual(detail_serializer.validated_data["job"]["job_number"], 4444)
        self.assertEqual(
            detail_serializer.validated_data["job"]["customer"]["name"], "test"
        )
        self.assertEqual(detail_serializer.validated_data["quantity"], 1)

    def test_job_validator_customer_blank(self):
        data = {
            "job": {"job_number": 4444},
            "machine": {"name": "Pinnacle 1"},
            "quantity": 1,
            "ltd_item_number": 1,
            "outsource_detail_number": "10",
        }
        job_serializer = DetailSerializer(data=data)

        self.assertRaises(
            ValidationError, job_serializer.is_valid, ["raise_exception", "true"]
        )

    def test_duplicate_detail_validation_error(self):
        data = {
            "job": {"job_number": 1111},
            "machine": {"name": "Pinnacle 1"},
            "quantity": 1,
            "ltd_item_number": 1,
            "outsource_detail_number": "10",
        }
        job_serializer = DetailSerializer(data=data)
        job_serializer.is_valid()
        job_serializer.save()

        job_serializer = DetailSerializer(data=data)

        self.assertRaises(
            ValidationError, job_serializer.is_valid, ["raise_exception", "true"]
        )
        self.assertEqual(
            job_serializer.errors["non_field_errors"][0],
            "1111 - Item 1 - Detail 10 already exists.",
        )
