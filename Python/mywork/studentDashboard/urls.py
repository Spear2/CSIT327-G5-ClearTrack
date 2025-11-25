from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_dashboard, name='student_dashboard'),
    path('logout/', views.student_logout, name='student_logout'),
    path('request-clearance/', views.request_clearance, name='request_clearance'),
    path('submission-history/', views.submission_history, name='submission_history'),
    path('download/<str:bucket_name>/<path:path>/', views.download_file, name='download_file'),
    path('profile/', views.profile_view, name='student_profile'),
    path('resubmit/<uuid:clearance_id>/', views.resubmit_clearance, name='resubmit_clearance'),
    path('profile-settings/', views.settings_profile, name='student_profile_settings'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('help-support/', views.help_support, name='help_support'),
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),
    path('faq/', views.faq_page, name='faq_page'),
    path('faqs/', views.FAQs_page, name='FAQs_page'),
]
