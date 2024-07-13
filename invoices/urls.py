from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('upload/', views.upload, name='upload'),
    path('dashboard/', views.dashboard, name='dashboard'),
]