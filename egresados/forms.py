from django import forms
from .models import Egresado, Carrera, CohorteIngresantes



class EgresadoForm(forms.ModelForm):
    class Meta:
        model = Egresado
        fields = [
            'numero_egresado',
            'nombres',
            'apellidos',
            'cin',
            'fecha_nacimiento',
            'lugar_nacimiento',
            'sexo',
            'carrera',
            'anio_ingreso',
            'anio_egreso',
            'link_repositorio',
        ]
        widgets = {
            'numero_egresado': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 298'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres completos'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos completos'}),
            'cin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 4500123'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'lugar_nacimiento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad / Departamento'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'carrera': forms.Select(attrs={'class': 'form-select'}),
            'anio_ingreso': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 2018'}),
            'anio_egreso': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 2024'}),
            'link_repositorio': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://publicaciones.fctunca.edu.py/handle/...'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        anio_ingreso = cleaned_data.get('anio_ingreso')
        anio_egreso = cleaned_data.get('anio_egreso')
        if anio_ingreso and anio_egreso and anio_egreso < anio_ingreso:
            self.add_error('anio_egreso', "El año de egreso no puede ser anterior al año de ingreso.")
        return cleaned_data


class CarreraForm(forms.ModelForm):
    class Meta:
        model = Carrera
        fields = ['nombre', 'duracion_teorica', 'activa']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Ingeniería Civil'}),
            'duracion_teorica': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '5'}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CohorteIngresantesForm(forms.ModelForm):
    class Meta:
        model = CohorteIngresantes
        fields = ['carrera', 'anio_cohorte', 'cantidad_masculino', 'cantidad_femenino', 'cantidad_ingresantes']
        widgets = {
            'carrera': forms.Select(attrs={'class': 'form-select'}),
            'anio_cohorte': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 2024'}),
            'cantidad_masculino': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'min': '0'}),
            'cantidad_femenino': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'min': '0'}),
            'cantidad_ingresantes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total automático si se deja en 0 o suma', 'min': '0'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        cant_m = cleaned_data.get('cantidad_masculino') or 0
        cant_f = cleaned_data.get('cantidad_femenino') or 0
        total = cleaned_data.get('cantidad_ingresantes') or 0

        # Si se especificaron valores por sexo y el total está vacío o en 0, calcularlo automáticamente
        if (cant_m > 0 or cant_f > 0) and (not total or total == 0):
            cleaned_data['cantidad_ingresantes'] = cant_m + cant_f
        elif total > 0 and (cant_m + cant_f > total):
            self.add_error('cantidad_ingresantes', "El total no puede ser inferior a la suma de ingresantes masculinos y femeninos.")

        return cleaned_data

