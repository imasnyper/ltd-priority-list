import graphene
from django.contrib.auth.models import User
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required

from list.models import Job, Customer, Machine


class JobType(DjangoObjectType):
    class Meta:
        model = Job


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer


class MachineType(DjangoObjectType):
    class Meta:
        model = Machine


class UserType(DjangoObjectType):
    class Meta:
        model = User


class Query(object):
    jobs = graphene.List(JobType, job_number=graphene.Int(), description=graphene.String())
    all_jobs = graphene.List(JobType)
    all_customers = graphene.List(CustomerType)
    all_machines = graphene.List(MachineType)
    all_users = graphene.List(UserType)

    @login_required
    def resolve_jobs(self, info, **kwargs):
        job_number = kwargs.get('job_number')
        description = kwargs.get('description')

        if job_number:
            job = Job.objects.filter(job_number=job_number)
            return job

        if description:
            job = Job.objects.filter(description=description)
            return job

    @login_required
    def resolve_all_jobs(self, info, **kwargs):
        return Job.objects.all()

    @login_required
    def resolve_all_customers(self, info, **kwargs):
        return Customer.objects.all()

    @login_required
    def resolve_all_machines(self, info, **kwargs):
        return Machine.objects.all()

    @login_required
    def resolve_all_users(self, info, **kwargs):
        return User.objects.all()