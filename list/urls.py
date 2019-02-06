from django.contrib.auth.decorators import login_required
from django.urls import path

from list import views

app_name = "list"

urlpatterns = [
    path('', views.PriorityListView.as_view(), name='priority-list'),
    path('job/add/<int:machine_pk>/', views.JobCreate.as_view(), name='add'),
    path('job/edit/<int:pk>/', views.JobUpdate.as_view(), name='edit'),
    path('job/sort_up/<int:pk>/', views.job_sort_up, name='sort_up'),
    path('job/sort_down/<int:pk>/', views.job_sort_down, name='sort_down'),
    path('job/archive/<int:pk>/', views.job_archive, name='archive'),
    path('archive', login_required(views.ArchiveView.as_view()), name='archive-view'),
    path('customer/add/',
         views.CustomerCreate.as_view(), name='add_customer'),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL,
#                           document_root=settings.STATIC_ROOT)
