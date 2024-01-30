from django.contrib import admin
from django.urls import path, include
from home import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', views.index, name='index'),
    path('about', views.about, name='about'),
    path('resume_upload', login_required(views.resume_upload), name='resume_upload'),
    path('login', views.Login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout_view, name='logout'),
    path('stream', views.stream, name='stream'),
]
