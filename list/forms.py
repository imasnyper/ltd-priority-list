from django import forms
from django.conf import settings
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe

from list.models import Job, Customer


class RelatedFieldWidgetCanAdd(forms.widgets.Select):

    def __init__(self, related_model, related_url=None, *args, **kw):

        super(RelatedFieldWidgetCanAdd, self).__init__(*args, **kw)

        if not related_url:
            rel_to = related_model
            info = (rel_to._meta.app_label, rel_to._meta.object_name.lower())
            related_url = '%s:add_%s' % info

        # Be careful that here "reverse" is not allowed
        self.related_url = related_url

    def render(self, name, value, *args, **kwargs):
        related_url = reverse_lazy(self.related_url)
        output = [super(RelatedFieldWidgetCanAdd, self).render(
            name, value, *args, **kwargs),
            '<a href="%s" class="add-another" id="add_id_%s" onclick="return showAddAnotherPopup(this);"> ' %
            (related_url, name), '<img src="%slist/img/icon-addlink.svg" width="15" height="15" alt="%s"/></a>' %
            (settings.STATIC_URL, 'Add Another')]
        return mark_safe(''.join(output))


class JobForm(forms.ModelForm):
    customer = forms.ModelChoiceField(
        required=True,
        queryset=Customer.objects.all(),
        widget=RelatedFieldWidgetCanAdd(Customer)
    )
    job_number = forms.CharField(
        label="Job Number:",
        widget=forms.TextInput(
            attrs={'min': 1000, 'max': 9999, 'type': 'number'}))
    due_date = forms.DateField(
        label="Due Date:",
        widget=forms.widgets.DateInput(attrs={'type': 'date'}),
        required=False)
    machine = forms.IntegerField(
        label="Machine:",
        required=False,
    )

    class Meta:
        model = Job
        fields = ['job_number', 'description',
                  'customer', 'machine', 'due_date', 'add_tools']


class CustomerForm(forms.ModelForm):

    class Meta:
        model = Customer
        fields = ["name", ]

    def clean_name(self):
        name = self.cleaned_data['name']
        customer_names = [cust.name for cust in Customer.objects.all()]
        if name.lower() in customer_names:
            raise forms.ValidationError("This customer already exists.")

        return name
