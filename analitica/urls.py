from django.urls import path
from . import views

app_name = 'analitica'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('tasas-cohorte/', views.tasas_cohorte_vista, name='tasas_cohorte'),
]
