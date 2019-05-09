from django import forms
from django.contrib.auth.models import User

from vacation_calendar.models import Vacation


class VacationForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.widgets.Select(attrs={'class': 'uk-select'}),
        required=True,
    )
    start_date = forms.DateField(
        widget=forms.widgets.DateInput(attrs={'class': 'uk-input date-input'})
    )
    end_date = forms.DateField(
        widget=forms.widgets.DateInput(attrs={'class': 'uk-input date-input'})
    )

    class Meta:
        model = Vacation
        fields = ('user', 'start_date', 'end_date')
