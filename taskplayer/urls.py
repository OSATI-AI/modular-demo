from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('load_task/', views.load_task, name='load_task'),
    path('send_message/', views.send_message, name='send_message'),
    path('generate', views.generate, name='generate'),
    path('generator_message', views.generator_message, name='generator_message'),
    path('save_task', views.save_task, name='save_task'),
]