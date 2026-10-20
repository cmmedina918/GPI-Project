from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from egresados.models import Egresado, Carrera, CohorteIngresantes


class Command(BaseCommand):
    help = "Crea y configura los roles y permisos estándar para el control de acceso en GPIProject"

    def handle(self, *args, **options):
        self.stdout.write("Configurando roles institucionales y permisos...")

        # Obtener content types
        ct_egresado = ContentType.objects.get_for_model(Egresado)
        ct_carrera = ContentType.objects.get_for_model(Carrera)
        ct_cohorte = ContentType.objects.get_for_model(CohorteIngresantes)

        # Permisos relevantes
        perm_view_egresado = Permission.objects.get(content_type=ct_egresado, codename='view_egresado')
        perm_add_egresado = Permission.objects.get(content_type=ct_egresado, codename='add_egresado')
        perm_change_egresado = Permission.objects.get(content_type=ct_egresado, codename='change_egresado')
        perm_delete_egresado = Permission.objects.get(content_type=ct_egresado, codename='delete_egresado')

        perm_view_carrera = Permission.objects.get(content_type=ct_carrera, codename='view_carrera')
        perm_add_carrera = Permission.objects.get(content_type=ct_carrera, codename='add_carrera')
        perm_change_carrera = Permission.objects.get(content_type=ct_carrera, codename='change_carrera')

        perm_view_cohorte = Permission.objects.get(content_type=ct_cohorte, codename='view_cohorteingresantes')
        perm_add_cohorte = Permission.objects.get(content_type=ct_cohorte, codename='add_cohorteingresantes')
        perm_change_cohorte = Permission.objects.get(content_type=ct_cohorte, codename='change_cohorteingresantes')
        perm_delete_cohorte = Permission.objects.get(content_type=ct_cohorte, codename='delete_cohorteingresantes')

        # 1. Rol: admin_general
        # El middleware ya otorga bypass total a este grupo o superusuarios,
        # pero también le asignamos todos los permisos para coherencia con Django admin.
        grupo_admin, _ = Group.objects.get_or_create(name='admin_general')
        grupo_admin.permissions.set(Permission.objects.all())
        self.stdout.write(self.style.SUCCESS("[OK] Rol 'admin_general' configurado."))

        # 2. Rol: coordinador_academico
        # Acceso analítico, consulta completa, alta y edición de egresados y cohortes
        grupo_coord, _ = Group.objects.get_or_create(name='coordinador_academico')
        grupo_coord.permissions.set([
            perm_view_egresado, perm_add_egresado, perm_change_egresado,
            perm_view_carrera,
            perm_view_cohorte, perm_add_cohorte, perm_change_cohorte
        ])
        self.stdout.write(self.style.SUCCESS("[OK] Rol 'coordinador_academico' configurado."))

        # 3. Rol: operador_registro
        # Carga y modificación de egresados y cohortes (sin eliminación)
        grupo_operador, _ = Group.objects.get_or_create(name='operador_registro')
        grupo_operador.permissions.set([
            perm_view_egresado, perm_add_egresado, perm_change_egresado,
            perm_view_carrera,
            perm_view_cohorte, perm_add_cohorte
        ])
        self.stdout.write(self.style.SUCCESS("[OK] Rol 'operador_registro' configurado."))

        # 4. Rol: auditor_consulta
        # Solo lectura para informes, tableros analíticos y padrones
        grupo_auditor, _ = Group.objects.get_or_create(name='auditor_consulta')
        grupo_auditor.permissions.set([
            perm_view_egresado,
            perm_view_carrera,
            perm_view_cohorte
        ])
        self.stdout.write(self.style.SUCCESS("[OK] Rol 'auditor_consulta' configurado."))

        self.stdout.write(self.style.SUCCESS("\nRoles y permisos sincronizados correctamente."))
