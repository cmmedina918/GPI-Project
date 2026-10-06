from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Egresado, Carrera
from .forms import EgresadoForm, CarreraForm


def lista_egresados(request):
    query = request.GET.get('q', '').strip()
    carrera_id = request.GET.get('carrera', '')
    sexo = request.GET.get('sexo', '')
    anio_egreso = request.GET.get('anio_egreso', '')

    egresados_qs = Egresado.objects.select_related('carrera').all()

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
