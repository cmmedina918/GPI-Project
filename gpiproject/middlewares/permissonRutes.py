"""
Mapa de Permisos por Rutas del Proyecto GPIProject
==================================================
Define los permisos requeridos para acceder a cada URL name o qualified name (app_name:url_name),
y la lista de rutas públicas accesibles sin autenticación previa.
"""

# Rutas protegidas y el permiso de Django nativo que requieren
MAPA_PERMISOS_RUTAS = {
    # ── Módulo Analítica Académica ──────────────────────────────────────────────
    'dashboard': 'egresados.view_egresado',
    'tasas_cohorte': 'egresados.view_cohorteingresantes',
    'analitica:dashboard': 'egresados.view_egresado',
    'analitica:tasas_cohorte': 'egresados.view_cohorteingresantes',

    # ── Módulo Egresados ────────────────────────────────────────────────────────
    'lista': 'egresados.view_egresado',
    'egresados:lista': 'egresados.view_egresado',
    'detalle': 'egresados.view_egresado',
    'egresados:detalle': 'egresados.view_egresado',
    'crear': 'egresados.add_egresado',
    'egresados:crear': 'egresados.add_egresado',
    'editar': 'egresados.change_egresado',
    'egresados:editar': 'egresados.change_egresado',

    # Carreras
    'carreras': 'egresados.view_carrera',
    'egresados:carreras': 'egresados.view_carrera',

    # Cohortes de Ingresantes
    'cohortes': 'egresados.view_cohorteingresantes',
    'egresados:cohortes': 'egresados.view_cohorteingresantes',
    'crear_cohorte': 'egresados.add_cohorteingresantes',
    'egresados:crear_cohorte': 'egresados.add_cohorteingresantes',
    'editar_cohorte': 'egresados.change_cohorteingresantes',
    'egresados:editar_cohorte': 'egresados.change_cohorteingresantes',
    'eliminar_cohorte': 'egresados.delete_cohorteingresantes',
    'egresados:eliminar_cohorte': 'egresados.delete_cohorteingresantes',
}

# Rutas públicas que no requieren autenticación
RUTAS_PUBLICAS = [
    'login',
    'logout',
    'password_reset',
    'password_reset_done',
    'password_reset_confirm',
    'password_reset_complete',
]
