from django.contrib.auth.decorators import login_required
from django.urls import path

from vacation_calendar import views

app_name = 'vacation'

urlpatterns = [
    path('', login_required(views.CalendarView.as_view()), name='calendar'),
    path('add/', login_required(views.VacationAdd.as_view()), name='add'),
    path('edit/<int:pk>/', login_required(views.VacationEdit.as_view()), name='edit'),
    path('delete/<int:pk>/', login_required(views.VacationDelete.as_view()), name='delete'),
]
