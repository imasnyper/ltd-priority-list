from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from list.models import Job, Detail, Machine, Customer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "groups"]


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]


class MachineSerializer(serializers.ModelSerializer):
    name = serializers.CharField(validators=[])

    class Meta:
        model = Machine
        fields = ["name"]


class CustomerSerializer(serializers.ModelSerializer):
    name = serializers.CharField(validators=[])

    class Meta:
        model = Customer
        fields = ["name"]


class JobSerializer(serializers.ModelSerializer):
    job_number = serializers.IntegerField(required=True)
    customer = CustomerSerializer(many=False, required=False)

    class Meta:
        model = Job
        fields = ["job_number", "customer"]


class DetailSerializer(serializers.ModelSerializer):
    job = JobSerializer(many=False, read_only=False, validators=[])
    machine = MachineSerializer(
        many=False, read_only=False, required=False, validators=[]
    )

    class Meta:
        model = Detail
        fields = [
            "job",
            "machine",
            "quantity",
            "ltd_item_number",
            "outsource_detail_number",
        ]

    def validate(self, data):
        if "customer" not in data["job"].keys():
            try:
                Job.objects.get(job_number=data["job"]["job_number"])
            except Job.DoesNotExist:
                raise serializers.ValidationError(
                    "Customer may not be blank if job doesn't exist."
                )

        try:
            job_number = data["job"]["job_number"]
            item_number = data["ltd_item_number"]
            detail_number = data["outsource_detail_number"]
            Detail.objects.get(
                job__job_number=job_number,
                ltd_item_number=item_number,
                outsource_detail_number=detail_number,
            )
            raise ValidationError(
                f"{job_number} - Item {item_number} - Detail {detail_number} already exists."
            )
        except Detail.DoesNotExist:
            # detail with this job number, item number and detail number
            # doesn't exist, so we're free to create one
            pass
        return data

    def validate_job(self, value):
        if value["job_number"] < 1000 or value["job_number"] > 9999:
            raise serializers.ValidationError(
                "The job number must be between 1000 and 9999"
            )

        return value

    def validate_machine(self, value):
        if value is not None:
            try:
                Machine.objects.get(name=value["name"])
            except Machine.DoesNotExist:
                raise serializers.ValidationError("The machine does not exist.")

        return value

    def create(self, validated_data):
        job_data = validated_data.pop("job")
        job_number = job_data.pop("job_number")
        customer = job_data.get("customer", None)
        machine = validated_data.get("machine", None)
        quantity = validated_data.pop("quantity")
        ltd_item_number = validated_data.pop("ltd_item_number")
        outsource_detail_number = validated_data.pop("outsource_detail_number")
        detail = Detail(
            ltd_item_number=ltd_item_number,
            outsource_detail_number=outsource_detail_number,
        )
        if customer is not None:
            customer, customer_created = Customer.objects.get_or_create(
                name__iexact=customer["name"]
            )
            job, job_created = Job.objects.get_or_create(
                job_number=job_number, customer=customer
            )
        else:
            job = Job.objects.get(job_number=job_number)

        detail.job = job

        if machine is not None:
            machine = Machine.objects.get(name=machine["name"])
            detail.machine = machine

        detail.quantity = quantity
        detail.save()
        return detail
