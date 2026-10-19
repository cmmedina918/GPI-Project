from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, F

from egresados.forms import EgresadoForm, CarreraForm, CohorteIngresantesForm
from egresados.models import Egresado, Carrera, CohorteIngresantes



def lista_egresados(request):
    query = request.GET.get('q', '').strip()
    carrera_id = request.GET.get('carrera', '')
    sexo = request.GET.get('sexo', '')
    anio_egreso = request.GET.get('anio_egreso', '')
    orden = request.GET.get('orden', 'numero_egresado')
    direccion = request.GET.get('dir', 'asc')

    egresados_qs = Egresado.objects.select_related('carrera').annotate(
        duracion_calculada=F('anio_egreso') - F('anio_ingreso') + 1
    )

    if query:
        egresados_qs = egresados_qs.filter(
            Q(nombres__icontains=query) |
            Q(apellidos__icontains=query) |
            Q(cin__icontains=query) |
            Q(lugar_nacimiento__icontains=query) |
            Q(numero_egresado__icontains=query)
        )

    if carrera_id:
        egresados_qs = egresados_qs.filter(carrera_id=carrera_id)

    if sexo:
        egresados_qs = egresados_qs.filter(sexo=sexo)

    if anio_egreso:
        egresados_qs = egresados_qs.filter(anio_egreso=anio_egreso)

    # Mapeo seguro de campos para ordenamiento
    orden_campos = {
        'numero': 'numero_egresado',
        'numero_egresado': 'numero_egresado',
        'egresado': 'apellidos',
        'apellidos': 'apellidos',
        'cin': 'cin',
        'carrera': 'carrera__nombre',
        'sexo': 'sexo',
        'cursado': 'anio_egreso',
        'anio_egreso': 'anio_egreso',
        'permanencia': 'duracion_calculada',
        'origen': 'lugar_nacimiento',
        'lugar_nacimiento': 'lugar_nacimiento',
    }

    campo_db = orden_campos.get(orden, 'numero_egresado')
    if direccion == 'desc':
        egresados_qs = egresados_qs.order_by(f"-{campo_db}", '-numero_egresado')
    else:
        egresados_qs = egresados_qs.order_by(campo_db, 'numero_egresado')

    paginator = Paginator(egresados_qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    carreras = Carrera.objects.all()
    anios_egreso = Egresado.objects.values_list('anio_egreso', flat=True).distinct().order_by('-anio_egreso')

    context = {
        'page_obj': page_obj,
        'carreras': carreras,
        'anios_egreso': anios_egreso,
        'query': query,
        'carrera_id': carrera_id,
        'sexo': sexo,
        'anio_egreso': anio_egreso,
        'orden': orden,
        'direccion': direccion,
        'total_registros': egresados_qs.count(),
    }
    return render(request, 'egresados/lista_egresados.html', context)


def crear_egresado(request):
    if request.method == 'POST':
        form = EgresadoForm(request.POST)
        if form.is_valid():
            egresado = form.save()
            messages.success(request, f"Egresado #{egresado.numero_egresado} {egresado.nombres} {egresado.apellidos} registrado exitosamente.")
            return redirect('egresados:lista')
        else:
            messages.error(request, "Por favor corrija los errores indicados en el formulario.")
    else:
        # Sugerir siguiente número de egresado
        ultimo = Egresado.objects.order_by('-numero_egresado').first()
        siguiente_num = (ultimo.numero_egresado + 1) if ultimo else 1
        form = EgresadoForm(initial={'numero_egresado': siguiente_num})

    return render(request, 'egresados/formulario_egresado.html', {'form': form, 'titulo': 'Registrar Nuevo Egresado'})


def editar_egresado(request, numero_egresado):
    egresado = get_object_or_404(Egresado, numero_egresado=numero_egresado)
    if request.method == 'POST':
        form = EgresadoForm(request.POST, instance=egresado)
        if form.is_valid():
            form.save()
            messages.success(request, f"Egresado #{egresado.numero_egresado} actualizado correctamente.")
            return redirect('egresados:lista')
        else:
            messages.error(request, "Por favor corrija los errores indicados en el formulario.")
    else:
        form = EgresadoForm(instance=egresado)

    return render(request, 'egresados/formulario_egresado.html', {
        'form': form,
        'egresado': egresado,
        'titulo': f'Editar Egresado #{egresado.numero_egresado}'
    })


def detalle_egresado(request, numero_egresado):
    egresado = get_object_or_404(Egresado.objects.select_related('carrera'), numero_egresado=numero_egresado)
    return render(request, 'egresados/detalle_egresado.html', {'egresado': egresado})


def lista_carreras(request):
    carreras = Carrera.objects.all()
    if request.method == 'POST':
        form = CarreraForm(request.POST)
        if form.is_valid():
            carrera = form.save()
            messages.success(request, f"Carrera '{carrera.nombre}' creada con éxito.")
            return redirect('egresados:carreras')
    else:
        form = CarreraForm()

    return render(request, 'egresados/carreras.html', {'carreras': carreras, 'form': form})


# ==============================================================================
# CRUD: Cohortes de Ingresantes (por Carrera, Año y Sexo)
# ==============================================================================

def lista_cohortes(request):
    carrera_id = request.GET.get('carrera', '')
    anio = request.GET.get('anio', '')

    cohortes_qs = CohorteIngresantes.objects.select_related('carrera').all()
    if carrera_id:
        cohortes_qs = cohortes_qs.filter(carrera_id=carrera_id)
    if anio:
        cohortes_qs = cohortes_qs.filter(anio_cohorte=anio)

    carreras = Carrera.objects.all()
    anios_disponibles = CohorteIngresantes.objects.values_list('anio_cohorte', flat=True).distinct().order_by('-anio_cohorte')

    paginator = Paginator(cohortes_qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Formulario para registro rápido
    form = CohorteIngresantesForm()

    context = {
        'page_obj': page_obj,
        'carreras': carreras,
        'anios_disponibles': anios_disponibles,
        'carrera_id': carrera_id,
        'anio': anio,
        'form': form,
        'total_cohortes': cohortes_qs.count(),
    }
    return render(request, 'egresados/cohortes.html', context)


def crear_cohorte(request):
    if request.method == 'POST':
        form = CohorteIngresantesForm(request.POST)
        if form.is_valid():
            cohorte = form.save()
            messages.success(request, f"Cohorte {cohorte.anio_cohorte} para {cohorte.carrera.nombre} registrada correctamente.")
            return redirect('egresados:cohortes')
        else:
            messages.error(request, "Error al registrar la cohorte. Revise los campos indicados.")
    else:
        form = CohorteIngresantesForm()

    carreras = Carrera.objects.all()
    return render(request, 'egresados/formulario_cohorte.html', {
        'form': form,
        'carreras': carreras,
        'titulo': 'Registrar Nueva Cohorte de Ingreso'
    })


def editar_cohorte(request, pk):
    cohorte = get_object_or_404(CohorteIngresantes, pk=pk)
    if request.method == 'POST':
        form = CohorteIngresantesForm(request.POST, instance=cohorte)
        if form.is_valid():
            form.save()
            messages.success(request, f"Cohorte {cohorte.anio_cohorte} de {cohorte.carrera.nombre} actualizada correctamente.")
            return redirect('egresados:cohortes')
        else:
            messages.error(request, "Error al actualizar la cohorte. Revise los datos ingresados.")
    else:
        form = CohorteIngresantesForm(instance=cohorte)

    return render(request, 'egresados/formulario_cohorte.html', {
        'form': form,
        'cohorte': cohorte,
        'titulo': f'Editar Cohorte {cohorte.anio_cohorte} - {cohorte.carrera.nombre}'
    })


def eliminar_cohorte(request, pk):
    cohorte = get_object_or_404(CohorteIngresantes, pk=pk)
    if request.method == 'POST':
        carrera_nombre = cohorte.carrera.nombre
        anio = cohorte.anio_cohorte
        cohorte.delete()
        messages.success(request, f"Cohorte {anio} de {carrera_nombre} eliminada exitosamente.")
        return redirect('egresados:cohortes')

    return render(request, 'egresados/confirmar_eliminar_cohorte.html', {'cohorte': cohorte})

