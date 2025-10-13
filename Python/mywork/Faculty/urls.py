from django.urls import path
from . import views

urlpatterns = [
    path('GradeFlow/', views.home, name='GradeFlow'),
    path('faculty_signin/', views.faculty_signin, name='faculty_signin'),
    path('faculty_signup/', views.faculty_signup, name = 'faculty_signup'),
    path('Dashboard/', views.homepage, name='homepage'),
    path('logout/', views.faculty_logout, name='faculty_logout'),
]