from django.contrib import admin
from django.urls import path, include
from myapp import views

urlpatterns = [
    path("", views.main , name = 'main'),
    path("new", views.main_2 , name = 'main_2')
]