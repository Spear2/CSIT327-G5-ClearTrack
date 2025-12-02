from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='GradeFlow'),
    path('faculty_signin/', views.faculty_signin, name='faculty_signin'),
    path('faculty_signup/', views.faculty_signup, name = 'faculty_signup'),
    path('faculty_Dashboard/', views.homepage, name='homepage'),
    path('logout/', views.faculty_logout, name='faculty_logout'),
    path('forogt_password', views.forgot_password, name='forgot_password'),
    path('new_password', views.new_password, name='new_password'),
    path('faculty_profile', views.faculty_profile, name ='faculty_profile'),
    path('faculty_security', views.faculty_security, name ='faculty_security'),
    path('add_comment/<uuid:document_id>/', views.add_comment, name='add_comment'),
    path('update_status/<uuid:document_id>/', views.update_status, name='update_status'),
    path('download/<str:bucket_name>/<path:path>/', views.download_file, name='download_file'),
    path('preview/<str:bucket_name>/<path:path>/', views.preview_file, name='preview_file'),
    path('help_and_support/', views.help_and_support, name='help_and_support'),
]