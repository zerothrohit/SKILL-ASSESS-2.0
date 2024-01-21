from django.contrib import admin
from django.urls import path,include
from home import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about', views.about, name='about'),
    path('resume_upload', views.resume_upload, name='resume_upload')
]