from django.urls import path

from . import views

app_name = "tracker"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("log/", views.log_list, name="log"),
    path("log/new/", views.log_create, name="log_create"),
    path("log/<int:pk>/delete/", views.log_delete, name="log_delete"),
    path("log/export.csv", views.log_export, name="log_export"),
    path("profile/", views.profile_edit, name="profile"),
    path("routines/", views.program_list, name="routines"),
    path("routines/<int:program_id>/", views.program_detail, name="program_detail"),
    path("routines/day/<int:day_id>/", views.day_detail, name="day_detail"),
    path("routines/day/<int:day_id>/start/", views.session_start, name="session_start"),
    path("session/<int:session_id>/", views.session_detail, name="session_detail"),
    path("session/<int:session_id>/finish/", views.session_finish, name="session_finish"),
    path("session/<int:session_id>/add-set/", views.session_add_set, name="session_add_set"),
    path("history/", views.history, name="history"),
]
