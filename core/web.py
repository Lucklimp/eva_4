"""Vistas web (templates) para login y dashboards con redirección por rol."""

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from .models import PLANES, Company, Subscription
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

    def dispatch(self, request, *args, **kwargs):
        plan_name = get_company_plan(request.user.company) if request.user.is_authenticated else None
        if request.user.is_authenticated and not plan_name:
            # Redirige al selector de plan si es el primer login o no tiene plan activo.
            return redirect("cliente_plan_selection")
        return super().dispatch(request, *args, **kwargs)


class ClientePlanSelectionView(RoleRequiredMixin, TemplateView):
    """Permite a clientes seleccionar un plan en su primer inicio."""

    template_name = "plan_selection.html"
    allowed_roles = ["cliente_final"]

    def post(self, request, *args, **kwargs):
        plan_name = request.POST.get("plan")
        if plan_name not in dict(PLANES):
            messages.error(request, "Debes elegir un plan válido.")
            return self.get(request, *args, **kwargs)

        company = request.user.company
        if not company:
            # Suposición: los clientes finales sin compañía obtienen una compañía propia.
            company = Company.objects.create(
                name=f"Cuenta {request.user.username}",
                rut=request.user.rut or "11.111.111-1",
                address="",
            )
            request.user.company = company
            request.user.save(update_fields=["company"])

        Subscription.objects.update_or_create(
            company=company,
            defaults={
                "plan_name": plan_name,
                # Suposición simple: plan activo por 30 días desde hoy. Ajustar según negocio real.
                "start_date": timezone.localdate(),
                "end_date": timezone.localdate() + timezone.timedelta(days=30),
                "active": True,
            },
        )

        messages.success(request, "Plan seleccionado correctamente.")
        return redirect("dashboard_cliente_final")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["plan_choices"] = PLANES
        return context


class ClientePlanDetailView(RoleRequiredMixin, TemplateView):
    """Muestra el plan actual y permite cambiarlo."""

    template_name = "my_plan.html"
    allowed_roles = ["cliente_final"]

    def post(self, request, *args, **kwargs):
        plan_name = request.POST.get("plan")
        if plan_name not in dict(PLANES):
            messages.error(request, "Selecciona un plan válido.")
            return self.get(request, *args, **kwargs)

        company = request.user.company
        if not company:
            messages.error(request, "No tienes una compañía asociada para el plan.")
            return redirect("cliente_plan_selection")

        Subscription.objects.update_or_create(
            company=company,
            defaults={
                "plan_name": plan_name,
                # Cambio inmediato: reinicia rango de fechas.
                "start_date": timezone.localdate(),
                "end_date": timezone.localdate() + timezone.timedelta(days=30),
                "active": True,
            },
        )
        messages.success(request, "Plan actualizado correctamente.")
        return redirect("cliente_plan_detail")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plan_name = get_company_plan(self.request.user.company)
        context.update({
            "plan_name": plan_name,
            "plan_choices": PLANES,
        })
        return context
