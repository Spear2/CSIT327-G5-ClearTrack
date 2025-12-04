from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.user_dashboard, name='admin_dashboard'),
    path('', views.user_login, name='admin_login'),
    path("students/", views.manage_students, name="manage_students"),
    path("students/delete/<int:id>/", views.delete_student, name="delete_student"),
    path("logout/", views.user_logout, name="admin_logout"),
    path('faculty/', views.manage_faculty, name="manage_faculty"),
    path("faculty/delete/<int:id>/", views.delete_faculty, name="delete_faculty"),
    path('add-faculty/', views.add_faculty, name='add_faculty'),
    path('add-student/', views.add_student, name='add_student'),
    path("notification/read/<int:id>/", views.mark_notification_read, name="mark_notification_read")


]
