from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='GradeFlow'),
    path('faculty_signin/', views.faculty_signin, name='faculty_signin'),
    path('faculty_signup/', views.faculty_signup, name = 'faculty_signup'),
    path('Dashboard/', views.homepage, name='homepage'),
    path('logout/', views.faculty_logout, name='faculty_logout'),
    path('forgot_password', views.forgot_password, name='forgot_password'),
    path('new_password', views.new_password, name='new_password'),
    path('faculty_profile', views.faculty_settings, name ='faculty_profile')
]