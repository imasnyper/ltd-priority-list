from django.contrib.auth.decorators import login_required
from django.urls import path

from list import views

app_name = "list"

urlpatterns = [
    path('', login_required(views.PriorityListView.as_view()), name='priority-list'),
    path('job/add/<int:machine_pk>/', login_required(views.JobCreate.as_view()), name='add'),
    path('job/edit/<int:pk>/', login_required(views.JobUpdate.as_view()), name='edit'),
    path('job/sort_up/<int:pk>/', login_required(views.job_sort_up), name='sort_up'),
    path('job/sort_down/<int:pk>/', login_required(views.job_sort_down), name='sort_down'),
    path('job/archive/<int:pk>/', login_required(views.job_archive), name='archive'),
    path('job/<int:pk>/', login_required(views.JobDetail.as_view()), name='job-detail'),
    path('archive/', login_required(views.ArchiveView.as_view()), name='archive-view'),
    path('customer/add/',
         login_required(views.CustomerCreate.as_view()), name='add_customer'),
    path('profile/<int:pk>/', login_required(views.ProfileView.as_view()), name='profile'),
    path('profile/edit/<int:pk>/', login_required(views.ProfileEditView.as_view()), name='profile-edit'),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL,
#                           document_root=settings.STATIC_ROOT)
