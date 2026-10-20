"""
Middlewares de Control de Acceso por Roles y Permisos
=======================================================
Este módulo implementa dos middlewares en cadena:

1. UserAccessInfoMiddleware
   - Se ejecuta PRIMERO en la cadena.
   - Inyecta `request.es_admin_general` en cada request autenticado.
   - Un usuario es admin_general si es superuser O pertenece al grupo 'admin_general'.

2. ControlAccesoMiddleware
   - Se ejecuta SEGUNDO, después del anterior.
   - Contrato de seguridad por capas (de más restrictivo a menos):
     a. Usuarios NO autenticados → solo pueden acceder a RUTAS_PUBLICAS.
        Cualquier otra ruta los redirige al login de Django vía LoginRequiredMixin/@login_required.
     b. Usuarios autenticados como admin_general → pasan sin restricciones (superusuario del sistema).
     c. Rutas en RUTAS_EXCLUSIVAS_ADMIN → solo admin_general. Si no, HTTP 403.
     d. Rutas en MAPA_PERMISOS_RUTAS → se valida has_perm(). Si no, HTTP 403.
     e. Rutas NO registradas en ninguna lista → pasan (rutas internas libres para usuarios autenticados).

Gap conocido y mitigado:
  - Las exportaciones (xlsx, pdf) no tienen URL propia — se gatillan con ?export=xlsx dentro de una
    vista ya protegida por el mapa. La verificación de permisos de exportación se realiza DENTRO
    de cada vista con has_perm(), devolviendo PermissionDenied si corresponde.
"""
import logging
from django.conf import settings
from django.shortcuts import redirect
from django.urls import resolve, reverse
from django.core.exceptions import PermissionDenied
from .permissonRutes import MAPA_PERMISOS_RUTAS, RUTAS_PUBLICAS

logger = logging.getLogger(__name__)

class UserAccessInfoMiddleware:
    """Inyecta `request.es_admin_general` para cada request autenticado."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # is_superuser de Django Y miembros del grupo 'admin_general' tienen acceso total.
            request.es_admin_general = (
                request.user.is_superuser
                or request.user.groups.filter(name='admin_general').exists()
            )
        else:
            request.es_admin_general = False

        return self.get_response(request)


class ControlAccesoMiddleware:
    """Verifica permisos por URL antes de despachar la vista."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # ── Paso 0: Resolver la URL actual ──────────────────────────────────────────
        try:
            url_match = resolve(request.path_info)
            url_name = url_match.url_name
            app_name = url_match.app_name  # Namespace de la app (puede ser '')
            # Construimos la clave cualificada para el admin de Django (ej: 'admin:index')
            qualified_name = f"{app_name}:{url_name}" if app_name else url_name
        except Exception:
            # URL no registrada (probablemente 404): dejamos que Django la maneje.
            return self.get_response(request)

        # ── Paso 1: Rutas públicas — accesibles sin autenticación ────────────────────
        if url_name in RUTAS_PUBLICAS or qualified_name in RUTAS_PUBLICAS:
            return self.get_response(request)

        # ── Paso 2: Forzar login para usuarios no autenticados ───────────────────────
        if not request.user.is_authenticated:
            login_url = getattr(settings, 'LOGIN_URL', 'login')
            try:
                redirect_to = reverse(login_url) + f"?next={request.path}"
            except Exception:
                redirect_to = f"/{login_url}/?next={request.path}"
            return redirect(redirect_to)

        # ── Paso 3: Admin general tiene acceso total ─────────────────────────────────
        es_admin_general = getattr(request, 'es_admin_general', False)
        if es_admin_general:
            return self.get_response(request)
        # ── Paso 4: Rutas con permiso específico requerido ───────────────────────────
        permiso_requerido = MAPA_PERMISOS_RUTAS.get(url_name) or MAPA_PERMISOS_RUTAS.get(qualified_name)
        if permiso_requerido and not request.user.has_perm(permiso_requerido):
            if settings.DEBUG:
                print("\n" + "-" * 30)
                print("🔒 [CONTROL DE ACCESO] - ACCESO INSUFICIENTE (403 Forbidden)")
                print(f"   👤 Usuario:           {request.user.username} (ID: {request.user.id})")
                print(f"   📍 Ruta solicitada:   {request.path}")
                print(f"   🎯 View Name / Key:   {url_name} " + (f"(Qualified: {qualified_name})" if app_name else ""))
                print(f"   🔑 PERMISO REQUERIDO: '{permiso_requerido}'")
                print("-" * 30 + "\n")

                # Opcional: registrarlo también en el sistema de logging estándar de Django
                logger.warning(
                    f"Acceso denegado a {request.user.username} para la ruta {request.path}. "
                    f"Requiere permiso: {permiso_requerido}"
                )

            raise PermissionDenied

        # ── Paso 5: Ruta autenticada libre (no clasificada) — dejar pasar ─────────────
        return self.get_response(request)
