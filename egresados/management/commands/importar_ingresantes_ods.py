import os
import zipfile
import xml.etree.ElementTree as ET
from django.core.management.base import BaseCommand
from django.conf import settings
from egresados.models import Carrera, CohorteIngresantes


class Command(BaseCommand):
    help = "Migra las cohortes de ingreso por carrera, año y sexo desde un archivo OpenDocument Spreadsheet (.ods)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='ingresantes.ods',
            help='Ruta al archivo .ods (por defecto: ingresantes.ods en la raíz del proyecto)'
        )

    def handle(self, *args, **options):
        ods_path = options['file']
        if not os.path.isabs(ods_path):
            ods_path = os.path.join(settings.BASE_DIR, ods_path)

        if not os.path.exists(ods_path):
            self.stderr.write(self.style.ERROR(f"No se encontró el archivo: {ods_path}"))
            return

        self.stdout.write(self.style.NOTICE(f"Abriendo y procesando archivo ODS: {ods_path}..."))

        try:
            with zipfile.ZipFile(ods_path, 'r') as z:
                content_xml = z.read('content.xml')
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error al leer el archivo ODS como archivo ZIP: {e}"))
            return

        tree = ET.fromstring(content_xml)
        ns = {
            'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
            'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'
        }

        tables = tree.findall('.//table:table', ns)
        if not tables:
            self.stderr.write(self.style.ERROR("No se encontraron tablas dentro del archivo .ods"))
            return

        # Cargar catálogo de carreras existentes o crearlas
        carreras_default = [
            'Ingeniería en Electricidad',
            'Ingeniería en Electrónica',
            'Ingeniería en Sistemas Informáticos',
            'Ingeniería Civil',
        ]
        carreras_map = {}
        for nombre in carreras_default:
            c_obj, _ = Carrera.objects.get_or_create(nombre=nombre, defaults={'duracion_teorica': 5, 'activa': True})
            carreras_map[nombre] = c_obj

        records = []
        current_carrera_nombre = None

        for t in tables:
            rows = t.findall('.//table:table-row', ns)
            for r in rows:
                cells = r.findall('.//table:table-cell', ns)
                row_vals = []
                for c in cells:
                    repeat = int(c.attrib.get('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}number-columns-repeated', 1))
                    texts = [p.text for p in c.findall('.//text:p', ns) if p.text]
                    val = ' '.join(texts).strip() if texts else ''
                    if repeat > 30:
                        continue
                    for _ in range(repeat):
                        row_vals.append(val)

                while row_vals and not row_vals[-1]:
                    row_vals.pop()

                if not row_vals:
                    continue

                # Detectar carrera en la fila
                for val in row_vals:
                    v_upper = val.upper()
                    if 'CIVIL' in v_upper:
                        current_carrera_nombre = 'Ingeniería Civil'
                    elif 'ELECTRICIDAD' in v_upper:
                        current_carrera_nombre = 'Ingeniería en Electricidad'
                    elif 'ELECTRONICA' in v_upper or 'ELECTRÓNICA' in v_upper:
                        current_carrera_nombre = 'Ingeniería en Electrónica'
                    elif 'INFORM' in v_upper:
                        current_carrera_nombre = 'Ingeniería en Sistemas Informáticos'

                # Ignorar encabezados
                if any(h in row_vals for h in ['VARONES', 'MUJERES', 'TOTAL', 'CARRERA']):
                    continue

                # Buscar año (entero de 4 dígitos entre 2000 y 2035)
                non_empty = [(i, val) for i, val in enumerate(row_vals) if val]
                for idx, (col_i, val) in enumerate(non_empty):
                    if val.isdigit() and len(val) == 4 and 2000 <= int(val) <= 2035:
                        if idx + 3 < len(non_empty):
                            try:
                                anio = int(val)
                                varones = int(non_empty[idx + 1][1])
                                mujeres = int(non_empty[idx + 2][1])
                                total = int(non_empty[idx + 3][1])
                                if current_carrera_nombre:
                                    records.append((current_carrera_nombre, anio, varones, mujeres, total))
                            except ValueError:
                                pass
                        break

        self.stdout.write(self.style.NOTICE(f"Se extrajeron {len(records)} registros de ingresantes desde el archivo."))

        creados = 0
        actualizados = 0

        for carrera_nombre, anio, varones, mujeres, total in records:
            carrera_obj = carreras_map.get(carrera_nombre)
            if not carrera_obj:
                carrera_obj, _ = Carrera.objects.get_or_create(nombre=carrera_nombre, defaults={'duracion_teorica': 5, 'activa': True})
                carreras_map[carrera_nombre] = carrera_obj

            cohorte, created = CohorteIngresantes.objects.update_or_create(
                carrera=carrera_obj,
                anio_cohorte=anio,
                defaults={
                    'cantidad_masculino': varones,
                    'cantidad_femenino': mujeres,
                    'cantidad_ingresantes': total,
                }
            )

            if created:
                creados += 1
            else:
                actualizados += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Migración completada exitosamente:\n"
                f" - {creados} cohortes creadas.\n"
                f" - {actualizados} cohortes actualizadas con datos por sexo (masculino/femenino).\n"
                f" - Total procesados: {len(records)} registros."
            )
        )
