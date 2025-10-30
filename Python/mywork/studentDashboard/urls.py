from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_dashboard, name='student_dashboard'),
    path('logout/', views.student_logout, name='student_logout'),
    path('request-clearance/', views.request_clearance, name='request_clearance'),
    path('submission-history/', views.submission_history, name='submission_history'),
    path('download/<str:bucket_name>/<path:path>/', views.download_file, name='download_file'),
    path('profile/', views.profile_view, name='student_profile'),

]
