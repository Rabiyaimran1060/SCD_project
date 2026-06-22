from django.urls import path
from . import views

urlpatterns = [
    path('', views.result_list, name='result_list'),
    path('add/', views.result_create, name='result_add'),
    path('<int:pk>/edit/', views.result_update, name='result_edit'),
    path('<int:pk>/delete/', views.result_delete, name='result_delete'),
]
