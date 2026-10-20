import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from egresados.models import Carrera, Egresado
from .services import calcular_indicadores_dashboard, calcular_tasas_graduacion_cohorte


@login_required
@permission_required('egresados.view_egresado', raise_exception=True)
def dashboard(request):
    carrera_id = request.GET.get('carrera')
    sexo = request.GET.get('sexo')
    anio_ingreso_desde = request.GET.get('anio_ingreso_desde')
    anio_ingreso_hasta = request.GET.get('anio_ingreso_hasta')
    anio_egreso_desde = request.GET.get('anio_egreso_desde')
    anio_egreso_hasta = request.GET.get('anio_egreso_hasta')
    ciudad = request.GET.get('ciudad')

    filtros = {}
    if carrera_id:
        filtros['carrera_id'] = int(carrera_id)
    if sexo:
        filtros['sexo'] = sexo
    if anio_ingreso_desde:
        filtros['anio_ingreso_desde'] = int(anio_ingreso_desde)
    if anio_ingreso_hasta:
        filtros['anio_ingreso_hasta'] = int(anio_ingreso_hasta)
    if anio_egreso_desde:
        filtros['anio_egreso_desde'] = int(anio_egreso_desde)
    if anio_egreso_hasta:
        filtros['anio_egreso_hasta'] = int(anio_egreso_hasta)
    if ciudad:
        filtros['ciudad'] = ciudad.strip()

    indicadores = calcular_indicadores_dashboard(filtros)
    tasas_graduacion = calcular_tasas_graduacion_cohorte(carrera_id=filtros.get('carrera_id'))

    carreras = Carrera.objects.all()
    ciudades = Egresado.objects.values_list('lugar_nacimiento', flat=True).distinct().order_by('lugar_nacimiento')

    # Datos estructurados en JSON para inicializar Chart.js
    chart_data = {
        'anios_egreso_labels': [str(item['anio_egreso']) for item in indicadores['egresados_por_anio']],
        'anios_egreso_values': [item['total'] for item in indicadores['egresados_por_anio']],
        'sexo_labels': ['Masculino', 'Femenino'],
        'sexo_values': [
            next((item['total'] for item in indicadores['egresados_por_sexo'] if item['sexo'] == 'M'), 0),
            next((item['total'] for item in indicadores['egresados_por_sexo'] if item['sexo'] == 'F'), 0),
        ],
        'carreras_labels': [item['carrera__nombre'] for item in indicadores['egresados_por_carrera']],
        'carreras_values': [item['total'] for item in indicadores['egresados_por_carrera']],
        'carrera_sexo': indicadores['carrera_sexo_data'],
        'duracion_labels': [f"{item['duracion']} años" for item in indicadores['distribucion_duracion']],
        'duracion_values': [item['total'] for item in indicadores['distribucion_duracion']],
        'duracion_ingreso_labels': [str(item['anio_ingreso']) for item in indicadores['duracion_por_ingreso']],
        'duracion_ingreso_values': [round(item['promedio_duracion'], 2) for item in indicadores['duracion_por_ingreso']],
        'edad_labels': [f"{item['edad']} años" for item in indicadores['edad_distribucion']],
        'edad_values': [item['total'] for item in indicadores['edad_distribucion']],
        'ciudades_labels': [item['lugar_nacimiento'] for item in indicadores['egresados_por_ciudad']],
        'ciudades_values': [item['total'] for item in indicadores['egresados_por_ciudad']],
    }

    context = {
        'filtros': filtros,
        'indicadores': indicadores,
        'tasas_graduacion': tasas_graduacion,
        'carreras': carreras,
        'ciudades': ciudades,
        'chart_data_json': json.dumps(chart_data),
    }
    return render(request, 'analitica/dashboard.html', context)


@login_required
@permission_required('egresados.view_cohorteingresantes', raise_exception=True)
def tasas_cohorte_vista(request):
    carrera_id = request.GET.get('carrera')
    carreras = Carrera.objects.all()
    tasas = calcular_tasas_graduacion_cohorte(carrera_id=int(carrera_id) if carrera_id else None)
    
    context = {
        'tasas': tasas,
        'carreras': carreras,
        'carrera_id': int(carrera_id) if carrera_id else None,
    }
    return render(request, 'analitica/tasas_cohorte.html', context)
