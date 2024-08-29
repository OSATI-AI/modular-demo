from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('load_task/', views.load_task, name='load_task'),
    path('send_message/', views.send_message, name='send_message'),
    path('generate', views.generate, name='generate'),
    path('generator_message', views.generator_message, name='generator_message'),
    path('save_task', views.save_task, name='save_task'),
    path('upload_image', views.upload_image, name='upload_image'),
    path('topic_lookup', views.topic_lookup, name='topic_lookup'),
    path('description', views.generate_description, name='description'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)