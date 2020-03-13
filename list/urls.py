from django.urls import path

from list import views

app_name = "list"

urlpatterns = [
    path("", views.PriorityListView.as_view(), name="priority-list"),
    path("job/add/<int:machine_pk>/", views.JobCreate.as_view(), name="add"),
    path(
        "job/<int:pk>/<int:machine_pk>/", views.JobDetail.as_view(), name="job-detail"
    ),
    path("job/<int:pk>/", views.JobDetail.as_view(), name="job-unassigned-details"),
    path("job/<int:pk>/", views.JobOverview.as_view(), name="job-overview"),
    path("job/edit/<int:pk>/", views.JobUpdate.as_view(), name="edit"),
    path("detail/<int:pk>/", views.DetailDetail.as_view(), name="detail"),
    path("search/", views.JobSearch.as_view(), name="search"),
    path(
        "job/sort_up/<int:job_pk>/<int:machine_pk>/", views.job_sort_up, name="sort_up"
    ),
    path(
        "job/sort_down/<int:job_pk>/<int:machine_pk>/",
        views.job_sort_down,
        name="sort_down",
    ),
    path(
        "job/to/<int:job_pk>/<int:machine_pk>/<int:to>/", views.job_to, name="job_to",
    ),
    path("job/archive/<int:pk>/", views.job_archive, name="archive"),
    path("archive/", views.ArchiveView.as_view(), name="archive-view"),
    path("customer/add/", views.CustomerCreate.as_view(), name="add_customer"),
    path("profile/<int:pk>/", views.ProfileView.as_view(), name="profile"),
    path(
        "profile/edit/<int:pk>/", views.ProfileEditView.as_view(), name="profile-edit"
    ),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL,
#                           document_root=settings.STATIC_ROOT)
