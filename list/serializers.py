from django.contrib.auth.models import User, Group
from rest_framework import serializers

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

    def validate(self, data):
        if "customer" not in data.keys():
            try:
                Job.objects.get(job_number=data["job_number"])
            except Job.DoesNotExist:
                raise serializers.ValidationError(
                    "Customer may not be blank if job doesn't exist."
                )
        return data

    # def validate_customer(self, value):
    #     if value is None:
    #         try:
    #             Job.objects.get(job_number=self.job_number)
    #         except Job.DoesNotExist:
    #             return serializers.ValidationError(
    #                 "Customer may only be blank if job already exists. Select a different job number, or input the Customer name for Customer object creation."
    #             )
    #     else:
    #         try:
    #             Job.objects.get(
    #                 job_number=self.job_number, customer__name__iexact=value
    #             )
    #         except Job.DoesNotExist:
    #             return serializers.ValidationError(
    #                 "Job matching given job number and customer name does not exist."
    #             )
    #
    #     return value


class DetailSerializer(serializers.ModelSerializer):
    job = JobSerializer(many=False, read_only=False, validators=[])
    machine = MachineSerializer(many=False, read_only=False, validators=[])

    class Meta:
        model = Detail
        fields = ["job", "machine", "ltd_item_number", "outsource_detail_number"]

    def validate_job(self, value):
        if value["job_number"] < 1000 or value["job_number"] > 9999:
            return serializers.ValidationError(
                "The job number must be between 1000 and 9999"
            )
        job = Job.objects.get(job_number=value["job_number"])
        if not job:
            return serializers.ValidationError("The job does not exist.")

        return value

    def validate_machine(self, value):
        machine = Machine.objects.get(name=value["name"])
        if not machine:
            return serializers.ValidationError("The machine does not exist.")

        return value

    def create(self, validated_data):
        job_data = validated_data.pop("job")
        job_number = job_data.pop("job_number")
        customer_name = job_data.pop("customer")["name"]
        machine_name = validated_data.pop("machine")["name"]
        ltd_item_number = validated_data.pop("ltd_item_number")
        outsource_detail_number = validated_data.pop("outsource_detail_number")
        detail = Detail(
            ltd_item_number=ltd_item_number,
            outsource_detail_number=outsource_detail_number,
        )
        customer, customer_created = Customer.objects.get_or_create(
            name__iexact=customer_name
        )
        job, job_created = Job.objects.get_or_create(
            job_number=job_number, customer=customer
        )
        machine = Machine.objects.get(name=machine_name)
        # serializer = DetailSerializer(data=)
        detail.job = job
        detail.machine = machine
        detail.save()
        return detail
