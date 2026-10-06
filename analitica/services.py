from django.db.models import Count, Avg, F, ExpressionWrapper, IntegerField, Q
from egresados.models import Egresado, Carrera, CohorteIngresantes


def calcular_indicadores_dashboard(filtros=None):
    filtros = filtros or {}
    qs = Egresado.objects.select_related('carrera').all()

    # Filtros multidimensionales
    if filtros.get('carrera_id'):
        qs = qs.filter(carrera_id=filtros['carrera_id'])
    if filtros.get('sexo'):
        qs = qs.filter(sexo=filtros['sexo'])
    if filtros.get('anio_ingreso_desde'):
        qs = qs.filter(anio_ingreso__gte=filtros['anio_ingreso_desde'])
    if filtros.get('anio_ingreso_hasta'):
        qs = qs.filter(anio_ingreso__lte=filtros['anio_ingreso_hasta'])
    if filtros.get('anio_egreso_desde'):
        qs = qs.filter(anio_egreso__gte=filtros['anio_egreso_desde'])
    if filtros.get('anio_egreso_hasta'):
        qs = qs.filter(anio_egreso__lte=filtros['anio_egreso_hasta'])
    if filtros.get('ciudad'):
        qs = qs.filter(lugar_nacimiento__icontains=filtros['ciudad'])

    total_egresados = qs.count()

    # 1. Egresados por año de egreso
    egresados_por_anio = list(
        qs.values('anio_egreso')
        .annotate(total=Count('numero_egresado'))
        .order_by('anio_egreso')
    )

    # 2. Egresados por sexo
    egresados_por_sexo = list(
        qs.values('sexo')
        .annotate(total=Count('numero_egresado'))
        .order_by('sexo')
    )

    # 3. Egresados por carrera
    egresados_por_carrera = list(
        qs.values('carrera__nombre')
        .annotate(total=Count('numero_egresado'))
        .order_by('-total')
    )

    # 4. Egresados por carrera y por sexo (Cruzado)
    carrera_sexo_raw = list(
        qs.values('carrera__nombre', 'sexo')
        .annotate(total=Count('numero_egresado'))
    )
    # Estructurar cruzado
    carreras_nombres = list(Carrera.objects.values_list('nombre', flat=True))
    carrera_sexo_data = {
        c: {'M': 0, 'F': 0} for c in carreras_nombres
    }
    for item in carrera_sexo_raw:
        c_nom = item['carrera__nombre']
        if c_nom in carrera_sexo_data:
            carrera_sexo_data[c_nom][item['sexo']] = item['total']

    # 5. Duración de carrera (Egreso - Ingreso)
    # Anotamos duracion
    qs_duracion = qs.annotate(
        duracion=ExpressionWrapper(F('anio_egreso') - F('anio_ingreso'), output_field=IntegerField())
    )
    distribucion_duracion = list(
        qs_duracion.values('duracion')
        .annotate(total=Count('numero_egresado'))
        .order_by('duracion')
    )
    promedio_duracion = qs_duracion.aggregate(prom=Avg('duracion'))['prom'] or 0

    # 6. Duración de carrera por año de ingreso
    duracion_por_ingreso = list(
        qs_duracion.values('anio_ingreso')
        .annotate(promedio_duracion=Avg('duracion'), total=Count('numero_egresado'))
        .order_by('anio_ingreso')
    )

    # 7. Edad al egreso
    # Para registros con fecha_nacimiento
    qs_con_fecha = qs.exclude(fecha_nacimiento__isnull=True)
    edad_list = []
    edad_distribucion = {}
    for eg in qs_con_fecha:
        edad = eg.anio_egreso - eg.fecha_nacimiento.year
        if 18 <= edad <= 70:
            edad_list.append(edad)
            edad_distribucion[edad] = edad_distribucion.get(edad, 0) + 1

    edad_promedio = (sum(edad_list) / len(edad_list)) if edad_list else 0
    edad_distribucion_sorted = [
        {'edad': edad, 'total': count} for edad, count in sorted(edad_distribucion.items())
    ]

    # 8. Egresados por ciudad de origen (Top 10 y otros)
    egresados_por_ciudad = list(
        qs.values('lugar_nacimiento')
        .annotate(total=Count('numero_egresado'))
        .order_by('-total')[:10]
    )

    return {
        'total_egresados': total_egresados,
        'egresados_por_anio': egresados_por_anio,
        'egresados_por_sexo': egresados_por_sexo,
        'egresados_por_carrera': egresados_por_carrera,
        'carrera_sexo_data': carrera_sexo_data,
        'distribucion_duracion': distribucion_duracion,
        'promedio_duracion': round(promedio_duracion, 2),
        'duracion_por_ingreso': duracion_por_ingreso,
        'edad_promedio': round(edad_promedio, 1),
        'edad_distribucion': edad_distribucion_sorted,
        'egresados_por_ciudad': egresados_por_ciudad,
    }


def calcular_tasas_graduacion_cohorte(carrera_id=None):
    """
    Calcula la tasa de graduación por cohorte y promedio histórico.
    TG(c, y) = (Egresados que ingresaron en 'y' / Ingresantes en 'y') * 100
    """
    carreras = Carrera.objects.all()
    if carrera_id:
        carreras = carreras.filter(id=carrera_id)

    resultados_carreras = []

    for carrera in carreras:
        cohortes = CohorteIngresantes.objects.filter(carrera=carrera).order_by('anio_cohorte')
        datos_cohortes = []
        tasas_list = []

        for ch in cohortes:
            # Egresados de esta carrera que ingresaron en este año
            egresados_cohorte = Egresado.objects.filter(
                carrera=carrera,
                anio_ingreso=ch.anio_cohorte
            ).count()

            ingresantes = ch.cantidad_ingresantes
            if ingresantes > 0:
                tasa = round((egresados_cohorte / ingresantes) * 100, 2)
                tasas_list.append(tasa)
            else:
                tasa = 0.0

            datos_cohortes.append({
                'anio_cohorte': ch.anio_cohorte,
                'ingresantes': ingresantes,
                'egresados': egresados_cohorte,
                'tasa': tasa,
            })

        tasa_promedio_historica = round(sum(tasas_list) / len(tasas_list), 2) if tasas_list else 0.0

        resultados_carreras.append({
            'carrera': carrera,
            'cohortes': datos_cohortes,
            'tasa_promedio_historica': tasa_promedio_historica,
        })

    return resultados_carreras
