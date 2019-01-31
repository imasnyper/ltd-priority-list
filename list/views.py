from django.shortcuts import redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from list.forms import CustomerForm, JobForm
from list.models import Customer, Job, Machine


# Create your views here.


class PriorityListView(ListView):
    model = Job
    template_name = "list/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['machines'] = Machine.objects.all()
        context['customers'] = Customer.objects.all().order_by("name")
        context['form'] = JobForm
        return context


class JobCreate(CreateView):
    model = Job
    success_url = reverse_lazy("list:priority-list")
    template_name = "list/index.html"
    form_class = JobForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['machines'] = Machine.objects.all()
        context['customers'] = Customer.objects.all()
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


class CustomerCreate(CreateView):
    model = Customer
    template_name = "list/add_customer.html"
    form_class = CustomerForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next_url'] = self.request.GET.get('next')
        context['current_customer'] = self.request.GET.get('cust')
        return context

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        else:
            return reverse("list:priority-list")


class JobUpdate(UpdateView):
    model = Job
    fields = ['add_tools', 'job_number', 'description', 'due_date', 'customer',
              'machine']
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
                                       'machine': job.machine.id})
        return context


def job_sort_up(request, pk):
    job = get_object_or_404(Job, pk=pk)

    job.up()
    job.save()

    return redirect(reverse("list:priority-list"))


def job_sort_down(request, pk):
    job = get_object_or_404(Job, pk=pk)

    job.down()
    job.save()

    return redirect(reverse("list:priority-list"))


class JobDelete(DeleteView):
    model = Job
    fields = ['job_number', 'description', 'customer']
    success_url = reverse_lazy("list:priority-list")
