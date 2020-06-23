from django.urls import path

from . import views

urlpatterns = [
    path('', views.InitialView.as_view(), name='initial'),
    path('index', views.QuestionView.as_view(), name='index'),
    path('restart', views.restart, name='restart'),
    path('about', views.about, name='about')
]
