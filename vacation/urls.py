from django.contrib.auth.decorators import login_required
from django.urls import path

from vacation import views

app_name = 'vacation'

urlpatterns = [
    path('', login_required(views.CalendarView.as_view()), name='calendar'),
    path('?year=<int:year>?month=<int:month>', login_required(views.CalendarView.as_view()), name='calendar'),
    path('<int:pk>/', login_required(views.VacationDetail.as_view()), name='detail'),
    path('add/', login_required(views.VacationAdd.as_view()), name='add'),
    path('add/?year=<int:year>?month=<int:month>?day=<int:day>',
         login_required(views.VacationAdd.as_view()), name='add'),
    path('edit/<int:pk>/', login_required(views.VacationEdit.as_view()), name='edit'),
    path('delete/<int:pk>/', login_required(views.VacationDelete.as_view()), name='delete'),
]
