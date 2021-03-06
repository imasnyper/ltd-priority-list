from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from list.models import Job, Customer, Machine, Profile


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
        output = [
            super(RelatedFieldWidgetCanAdd, self).render(name, value, *args,
                                                         **kwargs),
            '<a href="#" uk-toggle="target: #form-modal-customer">',
            '<span class="uk-text-success" uk-icon="plus"></span></a>'
        ]
        return mark_safe(''.join(output))


class JobForm(forms.ModelForm):
    customer = forms.ModelChoiceField(
        required=True,
        queryset=Customer.objects.all(),
        widget=RelatedFieldWidgetCanAdd(Customer, attrs={
            'class': 'uk-select uk-form-width-large'})
    )
    job_number = forms.CharField(
        label="Job Number:",
        widget=forms.TextInput(
            attrs={'min': 1000, 'max': 9999, 'type': 'number',
                   'class': 'uk-input'}))
    due_date = forms.DateField(
        label="Due Date:",
        widget=forms.widgets.DateInput(
            attrs={'type': 'text', 'class': 'uk-input date-input',
                   'data-uk-datepicker': "{format: 'MM/DD/YYYY'}"}),
        required=False)
    machine = forms.ModelChoiceField(
        label="Machine:",
        required=False,
        queryset=Machine.objects.all(),
        widget=forms.widgets.Select(attrs={'class': 'uk-select'})
    )
    add_tools = forms.BooleanField(
        widget=forms.widgets.CheckboxInput(attrs={'class': 'uk-checkbox'}),
        required=False,
    )
    description = forms.CharField(
        widget=forms.widgets.TextInput(attrs={'class': 'uk-input'})
    )
    active = forms.BooleanField(
        widget=forms.widgets.CheckboxInput(attrs={'class': 'uk-checkbox'}),
        required=False,
        initial=True
    )
    setup_sheets = forms.ChoiceField(
        label="Setup Sheets Completed:",
        required=False,
        choices=[("Y", "Yes"),
                 ("N", "No"),
                 ("-", "N/A")],
        widget=forms.widgets.Select(attrs={'class': 'uk-select'})
    )

    class Meta:
        model = Job
        fields = ['job_number', 'description',
                  'customer', 'machine', 'due_date', 'add_tools', 'active', 'setup_sheets']


class JobSearchForm(forms.ModelForm):
    customer = forms.ModelChoiceField(
        required=False,
        queryset=Customer.objects.all(),
        widget=RelatedFieldWidgetCanAdd(Customer, attrs={
            'class': 'uk-select uk-form-width-large'})
    )
    job_number = forms.CharField(
        required=False,
        label="Job Number:",
        widget=forms.TextInput(
            attrs={'min': 1000, 'max': 9999, 'type': 'number',
                   'class': 'uk-input'}))
    machine = forms.ModelChoiceField(
        label="Machine:",
        required=False,
        queryset=Machine.objects.all(),
        widget=forms.widgets.Select(attrs={'class': 'uk-select'})
    )
    description = forms.CharField(
        widget=forms.widgets.TextInput(attrs={'class': 'uk-input'}),
        required=False
    )
    due_date = forms.DateField(
        label="Due Date:",
        widget=forms.widgets.DateInput(
            attrs={'type': 'text', 'class': 'uk-input date-input',
                   'data-uk-datepicker': "{format: 'MM/DD/YYYY'}"}),
        required=False)
    due_date_lte = forms.BooleanField(
        label="Dates less than or equal to selected date",
        widget=forms.widgets.CheckboxInput(attrs={'class': 'uk-checkbox'}),
        required=False
    )
    due_date_gte = forms.BooleanField(
        label="Dates greater than or equal to selected date",
        widget=forms.widgets.CheckboxInput(attrs={'class': 'uk-checkbox'}),
        required=False
    )
    date_added = forms.DateField(
        label="Date Added:",
        widget=forms.widgets.DateInput(
            attrs={'type': 'text', 'class': 'uk-input date-input',
                   'data-uk-datepicker': "{format: 'MM/DD/YYYY'}"}),
        required=False)
    date_added_lte = forms.BooleanField(
        label="Dates less than or equal to selected date",
        widget=forms.widgets.CheckboxInput(attrs={'class': 'uk-checkbox'}),
        required=False
    )
    date_added_gte = forms.BooleanField(
        label="Dates greater than or equal to selected date",
        widget=forms.widgets.CheckboxInput(attrs={'class': 'uk-checkbox'}),
        required=False
    )
    datetime_completed = forms.DateField(
        label="Datetime Completed:",
        widget=forms.widgets.DateInput(
            attrs={'type': 'text', 'class': 'uk-input date-input',
                   'data-uk-datepicker': "{format: 'MM/DD/YYYY'}"}),
        required=False)
    datetime_completed_lte = forms.BooleanField(
        label="Dates less than or equal to selected date",
        widget=forms.widgets.CheckboxInput(attrs={'class': 'uk-checkbox'}),
        required=False
    )
    datetime_completed_gte = forms.BooleanField(
        label="Dates greater than or equal to selected date",
        widget=forms.widgets.CheckboxInput(attrs={'class': 'uk-checkbox'}),
        required=False
    )

    class Meta:
        model = Job
        fields = ['job_number', 'description',
                  'customer', 'machine', 'date_added', 'due_date',
                  'datetime_completed', 'date_added_lte', 'date_added_gte',
                  'due_date_lte', 'due_date_gte', 'datetime_completed_lte',
                  'datetime_completed_gte',
                  ]


class CustomerForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.widgets.TextInput(attrs={'class': 'uk-input'})
    )

    class Meta:
        model = Customer
        fields = ["name", ]

    def clean_name(self):
        name = self.cleaned_data['name']
        customer_names = [cust.name for cust in Customer.objects.all()]
        if name.lower() in customer_names:
            raise forms.ValidationError("This customer already exists.")

        return name


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('machines',)
        labels = {
            'machines': _("Select machines to display"),
        }
        widgets = {
            'machines': forms.SelectMultiple(
                attrs={'size': "8", 'class': 'uk-select'})
        }
