from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('predict-all/', views.predict_all_view, name='predict_all'),
    path('retrain/', views.retrain_model_view, name='retrain_model'),
]
