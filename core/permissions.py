from rest_framework import permissions

class IsAdminClienteOrGerente(permissions.BasePermission):
    """ Permiso para Jefes (Admin Cliente y Gerente) """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin_cliente', 'gerente', 'super_admin']

class IsVendedor(permissions.BasePermission):
    """ Permiso para Vendedores """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'vendedor'

class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'super_admin'