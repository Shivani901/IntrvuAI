from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('interview/', views.interview, name='interview'),
    path('start-interview/', views.start_interview, name='start_interview'),
    path('resume-upload/', views.resume_upload, name='resume_upload'),
    path('feedback/', views.feedback, name='feedback'),
    path('logout/', views.logout_view, name='logout'),
    path('submit-answers/', views.submit_answers, name='submit_answers'),
    path('history/', views.history, name='history'),
    path('profile/', views.profile, name='profile'),
    path('api/detect_emotion/', views.api_detect_emotion, name='api_detect_emotion'),
] 