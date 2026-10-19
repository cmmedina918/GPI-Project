from django.urls import path
from . import views

app_name = 'egresados'

urlpatterns = [
    path('', views.lista_egresados, name='lista'),
    path('nuevo/', views.crear_egresado, name='crear'),
    path('<int:numero_egresado>/', views.detalle_egresado, name='detalle'),
    path('<int:numero_egresado>/editar/', views.editar_egresado, name='editar'),
    path('carreras/', views.lista_carreras, name='carreras'),
    path('cohortes/', views.lista_cohortes, name='cohortes'),
    path('cohortes/nueva/', views.crear_cohorte, name='crear_cohorte'),
    path('cohortes/<int:pk>/editar/', views.editar_cohorte, name='editar_cohorte'),
    path('cohortes/<int:pk>/eliminar/', views.eliminar_cohorte, name='eliminar_cohorte'),
]
