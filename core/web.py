"""Vistas web (templates) para login y dashboards con redirección por rol."""

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from .permissions import RoleRequiredMixin
from .utils import build_menu_flags, get_company_plan


ROLE_DASHBOARD_URLS = {
    "super_admin": "dashboard_super_admin",
    "admin_cliente": "dashboard_admin_cliente",
    "gerente": "dashboard_gerente",
    "vendedor": "dashboard_vendedor",
    "cliente_final": "dashboard_cliente_final",
}


class RoleLoginView(View):
    template_name = "login.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if not user:
            messages.error(request, "Credenciales inválidas")
            return render(request, self.template_name, status=401)

        if not user.is_active:
            messages.error(request, "Usuario inactivo")
            return render(request, self.template_name, status=403)

        login(request, user)
        redirect_name = ROLE_DASHBOARD_URLS.get(user.role, "dashboard_vendedor")
        return redirect(reverse(redirect_name))


class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, "Sesión cerrada correctamente")
        return redirect("login")


class BaseDashboardView(RoleRequiredMixin, TemplateView):
    template_name = "dashboard.html"
    role_label = ""
    allowed_roles = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plan_name = get_company_plan(self.request.user.company) if self.request.user.is_authenticated else None
        context.update({
            "role_label": self.role_label,
            "plan_name": plan_name or "Sin Plan",
            "menu_flags": build_menu_flags(self.request.user.role, plan_name),
        })
        return context


class SuperAdminDashboardView(BaseDashboardView):
    allowed_roles = ["super_admin"]
    role_label = "Super Administrador"


class AdminClienteDashboardView(BaseDashboardView):
    allowed_roles = ["admin_cliente"]
    role_label = "Administrador de Tienda"


class GerenteDashboardView(BaseDashboardView):
    allowed_roles = ["gerente"]
    role_label = "Gerente"


class VendedorDashboardView(BaseDashboardView):
    allowed_roles = ["vendedor"]
    role_label = "Vendedor"


class ClienteFinalDashboardView(BaseDashboardView):
    allowed_roles = ["cliente_final"]
    role_label = "Cliente Final"
