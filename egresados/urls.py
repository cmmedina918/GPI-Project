from django.urls import path
from . import views

app_name = 'egresados'

urlpatterns = [
    path('', views.lista_egresados, name='lista'),
    path('nuevo/', views.crear_egresado, name='crear'),
    path('<int:numero_egresado>/', views.detalle_egresado, name='detalle'),
    path('<int:numero_egresado>/editar/', views.editar_egresado, name='editar'),
    path('carreras/', views.lista_carreras, name='carreras'),
]
