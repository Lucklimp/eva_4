from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from rest_framework import permissions

from .utils import has_feature


class IsAdminClienteOrGerente(permissions.BasePermission):
    """Permiso para Admin Cliente y Gerente (y Super Admin)."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin_cliente', 'gerente', 'super_admin']


class IsVendedor(permissions.BasePermission):
    """Permiso para Vendedores."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'vendedor'


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'super_admin'


class PlanFeaturePermission(permissions.BasePermission):
    """Valida si el plan asociado permite acceder a la funcionalidad."""

    required_feature = None

    def has_permission(self, request, view):
        feature = getattr(view, 'required_plan_feature', self.required_feature)
        if not feature:
            return True
        return has_feature(request.user, feature)


class RoleRequiredMixin:
    """Mixin reutilizable para vistas basadas en clase protegidas por rol."""

    allowed_roles = []

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if self.allowed_roles and request.user.role not in self.allowed_roles:
            messages.error(request, "No tienes permiso para acceder a este panel.")
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)
