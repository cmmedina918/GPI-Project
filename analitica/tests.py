from django.test import TestCase, Client
from django.urls import reverse
from egresados.models import Carrera, Egresado, CohorteIngresantes
from analitica.services import calcular_indicadores_dashboard, calcular_tasas_graduacion_cohorte


class EgresadosAnaliticaTests(TestCase):
    def setUp(self):
        self.carrera = Carrera.objects.create(nombre="Ingeniería Civil", duracion_teorica=5)
        self.egresado = Egresado.objects.create(
            numero_egresado=1,
            nombres="Juan",
            apellidos="Pérez",
            cin="1234567",
            lugar_nacimiento="Coronel Oviedo",
            sexo="M",
            carrera=self.carrera,
            anio_ingreso=2015,
            anio_egreso=2020,
        )
        self.cohorte = CohorteIngresantes.objects.create(
            carrera=self.carrera,
            anio_cohorte=2015,
            cantidad_ingresantes=10
        )
        self.client = Client()

    def test_modelo_egresado_propiedades(self):
        self.assertEqual(self.egresado.duracion_carrera, 5)

    def test_calculo_tasa_graduacion(self):
        tasas = calcular_tasas_graduacion_cohorte(carrera_id=self.carrera.id)
        self.assertEqual(len(tasas), 1)
        self.assertEqual(tasas[0]['tasa_promedio_historica'], 10.0)

    def test_vistas_dashboard_y_listas(self):
        resp_dashboard = self.client.get(reverse('analitica:dashboard'))
        self.assertEqual(resp_dashboard.status_code, 200)

        resp_tasas = self.client.get(reverse('analitica:tasas_cohorte'))
        self.assertEqual(resp_tasas.status_code, 200)

        resp_egresados = self.client.get(reverse('egresados:lista'))
        self.assertEqual(resp_egresados.status_code, 200)

        resp_carreras = self.client.get(reverse('egresados:carreras'))
        self.assertEqual(resp_carreras.status_code, 200)
