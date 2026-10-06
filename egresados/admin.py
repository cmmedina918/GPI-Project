from django.contrib import admin
from .models import Carrera, Egresado, CohorteIngresantes


@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'duracion_teorica', 'activa')
    list_filter = ('activa',)
    search_fields = ('nombre',)


@admin.register(Egresado)
class EgresadoAdmin(admin.ModelAdmin):
    list_display = (
        'numero_egresado',
        'apellidos',
        'nombres',
        'cin',
        'carrera',
        'sexo',
        'anio_ingreso',
        'anio_egreso',
        'lugar_nacimiento',
    )
    list_filter = ('carrera', 'sexo', 'anio_egreso', 'anio_ingreso')
    search_fields = ('numero_egresado', 'nombres', 'apellidos', 'cin', 'lugar_nacimiento')
    ordering = ('numero_egresado',)


@admin.register(CohorteIngresantes)
class CohorteIngresantesAdmin(admin.ModelAdmin):
    list_display = ('carrera', 'anio_cohorte', 'cantidad_ingresantes')
    list_filter = ('carrera', 'anio_cohorte')
    search_fields = ('carrera__nombre',)
    ordering = ('anio_cohorte', 'carrera')
