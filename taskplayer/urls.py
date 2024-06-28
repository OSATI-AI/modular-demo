from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('load_task/', views.load_task, name='load_task'),
    path('set_task_context/', views.set_task_context, name='set_task_context'),
    path('send_message/', views.send_message, name='send_message'),
]