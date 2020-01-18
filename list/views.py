from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from rest_framework import viewsets, status
from rest_framework.response import Response

from list.forms import CustomerForm, JobForm, ProfileForm, JobSearchForm
from list.models import Customer, Job, Machine, Profile, MachineOrder, Detail
from list.serializers import (
    UserSerializer,
    GroupSerializer,
    DetailSerializer,
    JobSerializer,
    MachineSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class DetailViewSet(viewsets.ModelViewSet):
    queryset = Detail.objects.all()
    serializer_class = DetailSerializer

    def create(self, request):
        try:
            job_instance = Job.objects.get(job_number=request.data["job.job_number"])
        except Job.DoesNotExist:
            print(request.data)
            if (
                request.data["job.customer.name"] is not None
                and request.data["job.customer.name"] != ""
            ):
                customer_instance, customer_created = Customer.objects.get_or_create(
                    name=request.data["job.customer.name"]
                )
                job_instance, job_created = Job.objects.get_or_create(
                    job_number=request.data["job.job_number"],
                    customer=customer_instance,
                )
            else:
                job_serializer = JobSerializer(
                    data={"job_number": request.data["job.job_number"]}
                )
                job_serializer.is_valid(raise_exception=True)

        machine_instance = Machine.objects.get(
            name__iexact=request.data["machine.name"]
        )
        machine_serializer = MachineSerializer(instance=machine_instance)

        job_serializer = JobSerializer(instance=job_instance)
        new_data = {
            "ltd_item_number": request.data["ltd_item_number"],
            "outsource_detail_number": request.data["outsource_detail_number"],
            "job": job_serializer.data,
            "machine": machine_serializer.data,
        }
        serializer = self.get_serializer(data=new_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def list(self, request):
        return super().list(request)


class PriorityListView(LoginRequiredMixin, ListView):
    model = Job
    template_name = "list/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = get_object_or_404(User, id=self.request.user.id)
        profile = get_object_or_404(Profile, user=user)

        context["machines"] = profile.machines.all()
        context["customers"] = Customer.objects.all().order_by("name")
        context["form"] = JobForm(auto_id="", initial={"setup_sheets": "N"})
        context["customer_form"] = CustomerForm()
        context["debug"] = settings.DEBUG

        return context


class JobCreate(LoginRequiredMixin, CreateView):
    model = Job
    success_url = reverse_lazy("list:priority-list")
    template_name = "list/index.html"
    form_class = JobForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["machines"] = Machine.objects.all()
        context["customers"] = Customer.objects.all()
        if self.request.method == "POST":
            if kwargs["form"].is_bound:
                context["active_machine"] = self.kwargs["machine_pk"]
                context["active_machine_form"] = context["form"]
                context["form"] = JobForm
            else:
                context["active_machine"] = None

        return context

    def form_valid(self, form):
        form.instance.machine = Machine.objects.get(pk=self.kwargs["machine_pk"])
        form.save()
        return super().form_valid(form)


class JobDetail(LoginRequiredMixin, DetailView):
    model = Job

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["details"] = self.object.details.filter(
            machine=self.kwargs["machine_pk"]
        ).order_by("ltd_item_number")
        context["machine"] = Machine.objects.get(pk=self.kwargs["machine_pk"])

        return context


class JobOverview(LoginRequiredMixin, DetailView):
    model = Job
    template_name = "list/job_overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["details"] = Detail.objects.filter(
            job=Job.objects.get(pk=self.kwargs["pk"])
        ).order_by("machine__name")
        context["machines"] = Machine.objects.filter(
            details__in=Detail.objects.filter(job=Job.objects.get(pk=self.kwargs["pk"]))
        )

        return context


class DetailDetail(LoginRequiredMixin, DetailView):
    model = Detail
    context_object_name = "detail"


class JobUpdate(LoginRequiredMixin, UpdateView):
    model = Job
    fields = [
        "add_tools",
        "job_number",
        "description",
        "due_date",
        "customer",
        "active",
        "setup_sheets",
    ]
    success_url = reverse_lazy("list:priority-list")
    template_name_suffix = "_update_form"

    def get_context_data(self, **kwargs):
        job = self.object
        context = super().get_context_data(**kwargs)
        context["customers"] = Customer.objects.all().order_by("name")
        context["job_form"] = JobForm(
            {
                "add_tools": job.add_tools,
                "job_number": job.job_number,
                "description": job.description,
                "due_date": job.due_date,
                "customer": job.customer.id,
                "active": job.active,
                "setup_sheets": job.setup_sheets,
            }
        )
        return context


class JobSearch(LoginRequiredMixin, ListView):
    model = Job
    template_name = "list/search.html"
    form_class = JobSearchForm
    context_object_name = "jobs"
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get = self.request.GET
        context["search_terms"] = {
            k: v for k, v in get.items() if v is not None and v != "" and k != "page"
        }
        context["search_form"] = self.form_class(context["search_terms"])

        # create key=value pairs for all search arguments that are not empty
        # join them all together with '&' for url args which will be added to
        # pagination links
        context["args"] = "&".join(
            [f"{k}={v}" for k, v in context["search_terms"].items()]
        )
        if len(context["args"]) > 0:
            context["args"] = "&" + context["args"]
        return context

    def get_queryset(self):
        form = self.form_class(self.request.GET)
        if form.is_valid():
            data = form.cleaned_data
            data = {k: v for k, v in data.items() if v is not None and v != ""}
            due_date_lte = data.pop("due_date_lte", False)
            due_date_gte = data.pop("due_date_gte", False)
            date_added_lte = data.pop("date_added_lte", False)
            date_added_gte = data.pop("date_added_gte", False)
            datetime_completed_lte = data.pop("datetime_completed_lte", False)
            datetime_completed_gte = data.pop("datetime_completed_gte", False)

            description = data.pop("description", None)
            datetime_completed = data.pop("datetime_completed", None)
            date_added = data.pop("date_added", None)
            due_date = data.pop("due_date", None)

            qs = Job.objects.filter(**data)
            if description is not None:
                qs = qs.filter(description__contains=description)
            if datetime_completed is not None:
                if datetime_completed_lte:
                    qs = qs.filter(datetime_completed__lte=datetime_completed)
                elif datetime_completed_gte:
                    qs = qs.filter(datetime_completed__gte=datetime_completed)
                else:
                    qs = qs.filter(datetime_completed__date=datetime_completed)
            if date_added is not None:
                if date_added_lte:
                    qs = qs.filter(date_added__lte=date_added)
                elif date_added_gte:
                    qs = qs.filter(date_added__gte=date_added)
                else:
                    qs = qs.filter(date_added__date=date_added)
            if due_date is not None:
                if due_date_lte:
                    qs = qs.filter(due_date__lte=due_date)
                elif due_date_gte:
                    qs = qs.filter(due_date__gte=due_date)
                else:
                    qs = qs.filter(due_date__date=due_date)
            return qs.order_by("date_added")
        return super().get_queryset()


class ArchiveView(LoginRequiredMixin, ListView):
    model = Job
    template_name = "list/archive.html"
    context_object_name = "jobs"
    paginate_by = 10

    def get_queryset(self):
        user = get_object_or_404(User, id=self.request.user.id)
        profile = get_object_or_404(Profile, user=user)

        return (
            Job.objects.all()
            .filter(active=False)
            .filter(details__machine__in=profile.machines.all())
            .order_by("-datetime_completed")
            .distinct()
        )


class CustomerCreate(LoginRequiredMixin, CreateView):
    model = Customer
    template_name = "list/add_customer.html"
    form_class = CustomerForm
    success_url = "list/index.html"


@login_required()
def job_sort_up(request, job_pk, machine_pk):
    job = get_object_or_404(Job, pk=job_pk)
    machine = get_object_or_404(Machine, pk=machine_pk)
    machine_order = get_object_or_404(MachineOrder, job=job, machine=machine)

    machine_order.up()

    return HttpResponseRedirect(reverse("list:priority-list"))


@login_required()
def job_sort_down(request, job_pk, machine_pk):
    job = get_object_or_404(Job, pk=job_pk)
    machine = get_object_or_404(Machine, pk=machine_pk)
    machine_order = get_object_or_404(MachineOrder, job=job, machine=machine)

    machine_order.down()

    return HttpResponseRedirect(reverse("list:priority-list"))


@login_required()
def job_to(request, job_pk, machine_pk, to):
    machine = get_object_or_404(Machine, pk=machine_pk)
    job = get_object_or_404(Job, pk=job_pk)
    machine_order = get_object_or_404(MachineOrder, machine=machine, job=job)

    machine_order.to(to)

    return HttpResponseRedirect(reverse("list:priority-list"))


@login_required()
def job_archive(request, pk):
    job = get_object_or_404(Job, pk=pk)

    job.active = False
    job.save()

    return redirect(reverse("list:priority-list"))


# class JobDelete(DeleteView):
#     model = Job
#     fields = ['job_number', 'description', 'customer']
#     success_url = reverse_lazy("list:priority-list")


class ProfileView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Profile
    template_name = "common/profile.html"

    def test_func(self):
        user = get_object_or_404(User, pk=self.request.resolver_match.kwargs["pk"])
        return user.username == self.request.user.username


class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "common/profile_update.html"

    def test_func(self):
        user = get_object_or_404(User, pk=self.request.resolver_match.kwargs["pk"])
        return user.username == self.request.user.username
