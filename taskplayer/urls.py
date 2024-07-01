from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('load_task/', views.load_task, name='load_task'),
    path('send_message/', views.send_message, name='send_message'),
]