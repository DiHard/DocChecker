from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('settings/', views.bot_settings, name='settings'),
    path('users/', views.users, name='users')
]
