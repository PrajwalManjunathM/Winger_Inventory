from django.contrib import admin
from django.urls import path, include
from app import views

urlpatterns = [
    path("", views.user_login , name = 'user_login'),
    path("admin_login/", views.admin_login, name = 'admin_login'),
    path("add_users/", views.add_users, name = 'add_users'),
    path("dashboard/", views.dashboard, name = 'dashboard'),
    path("home/", views.home , name = 'home'),
    path("home_2/", views.home_2 , name = 'home_2'),
    path("sell/", views.sell, name = 'sell'),
    path("rent/", views.rent, name = 'rent'),
    path("retrieve/", views.retrieve, name = 'retrieve'),
    path("add_to_inventory/", views.add_to_inventory, name = 'add_to_inventory'),
    path("routine_check/", views.routine_check_1, name = 'routine_check'),
    path("item_history/", views.item_history, name = 'item_history'),
    path("inventory/", views.inventory, name = 'inventory'),
    path("rented/", views.rented, name = 'rented'),
    path("sold/", views.sold, name = 'sold'),
    path("missing/", views.missing, name = 'missing'),
    path("warranty/", views.warranty, name = 'warranty'),
]

