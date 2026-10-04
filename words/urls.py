from django.urls import path

from . import views

app_name = 'words'

urlpatterns = [
    path('', views.words_list, name='list'),
    path('<int:word_id>/learn/', views.learn, name='learn'),
]
