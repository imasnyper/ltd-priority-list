from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from list.forms import CustomerForm, JobForm, ProfileForm, JobSearchForm
from list.models import Customer, Job, Machine, Profile


# Create your views here.


class PriorityListView(LoginRequiredMixin, ListView):
    model = Job
    template_name = "list/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = get_object_or_404(User, id=self.request.user.id)
        profile = get_object_or_404(Profile, user=user)

        context['machines'] = profile.machines.all()
        context['customers'] = Customer.objects.all().order_by("name")
        context['form'] = JobForm(auto_id="")
        context['customer_form'] = CustomerForm()
        context['debug'] = settings.DEBUG

        return context


class JobCreate(LoginRequiredMixin, CreateView):
    model = Job
    success_url = reverse_lazy("list:priority-list")
    template_name = "list/index.html"
    form_class = JobForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['machines'] = Machine.objects.all()
        context['customers'] = Customer.objects.all()
        if self.request.method == "POST":
            if kwargs['form'].is_bound:
                context['active_machine'] = self.kwargs['machine_pk']
                context['active_machine_form'] = context['form']
                context['form'] = JobForm
            else:
                context['active_machine'] = None

        return context

    def form_valid(self, form):
        form.instance.machine = Machine.objects.get(
            pk=self.kwargs['machine_pk'])
        form.save()
        return super().form_valid(form)


class JobDetail(LoginRequiredMixin, DetailView):
    model = Job


class JobUpdate(LoginRequiredMixin, UpdateView):
    model = Job
    fields = ['add_tools', 'job_number', 'description', 'due_date', 'customer',
              'machine', 'active']
    success_url = reverse_lazy("list:priority-list")
    template_name_suffix = "_update_form"

    def get_context_data(self, **kwargs):
        job = self.object
        context = super().get_context_data(**kwargs)
        context['machines'] = Machine.objects.all()
        context['customers'] = Customer.objects.all().order_by("name")
        context['job_form'] = JobForm({'add_tools': job.add_tools,
                                       'job_number': job.job_number,
                                       'description': job.description,
                                       'due_date': job.due_date,
                                       'customer': job.customer.id,
                                       'machine': job.machine.id,
                                       'active': job.active})
        return context


class JobSearch(LoginRequiredMixin, ListView):
    model = Job
    template_name = "list/search.html"
    form_class = JobSearchForm
    context_object_name = "jobs"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = self.form_class()
        return context

    def get_queryset(self):
        form = self.form_class(self.request.GET)
        if form.is_valid():
            if form.cleaned_data['job_number'] != '':
                job_number = form.cleaned_data['job_number']
            else:
                job_number = None
            if form.cleaned_data['add_tools'] != '':
                add_tools = form.cleaned_data['add_tools']
            else:
                add_tools = None
            return Job.objects.filter(
                job_number=job_number,
            )
        return Job.objects.all()

class ArchiveView(LoginRequiredMixin, ListView):
    model = Job
    template_name = "list/archive.html"
    context_object_name = "jobs"
    paginate_by = 10

    def get_queryset(self):
        user = get_object_or_404(User, id=self.request.user.id)
        profile = get_object_or_404(Profile, user=user)

        return Job.objects.all() \
            .filter(active=False) \
            .filter(machine__in=profile.machines.all()) \
            .order_by("-datetime_completed")


class CustomerCreate(LoginRequiredMixin, CreateView):
    model = Customer
    template_name = "list/add_customer.html"
    form_class = CustomerForm
    success_url = 'list/index.html'


@login_required()
def job_sort_up(request, pk):
    job = get_object_or_404(Job, pk=pk)

    job.up()
    job.save()

    return HttpResponseRedirect(reverse("list:priority-list"))

@login_required()
def job_sort_down(request, pk):
    job = get_object_or_404(Job, pk=pk)

    job.down()
    job.save()

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
        user = get_object_or_404(User, pk=self.request.resolver_match.kwargs['pk'])
        return user.username == self.request.user.username


class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "common/profile_update.html"

    def test_func(self):
        user = get_object_or_404(User, pk=self.request.resolver_match.kwargs['pk'])
        return user.username == self.request.user.username
