"""Utilidades comunes para manejo de planes y helpers de vistas."""

from typing import Optional, Union

from django.contrib.auth import get_user_model


PLAN_ORDER = ["Basico", "Estandar", "Premium"]

# Definición centralizada de features asociadas a planes.
PLAN_FEATURES = {
    "reports_standard": "Estandar",
    "reports_advanced": "Premium",
}


def plan_satisfies(plan_name: Optional[str], required: str) -> bool:
    """Indica si ``plan_name`` cumple con el plan mínimo requerido."""

    if not plan_name or plan_name not in PLAN_ORDER:
        return False

    try:
        return PLAN_ORDER.index(plan_name) >= PLAN_ORDER.index(required)
    except ValueError:
        return False


def get_company_plan(company) -> Optional[str]:
    """Obtiene el nombre del plan de la compañía si existe."""

    if not company:
        return None

    subscription = getattr(company, "subscription", None)
    if subscription and subscription.active:
        return subscription.plan_name
    return None


def get_branch_limit(plan_name: Optional[str]) -> Optional[int]:
    """Retorna el límite de sucursales según el plan (``None`` significa ilimitado)."""

    limits = {"Basico": 1, "Estandar": 3, "Premium": None}
    return limits.get(plan_name)


def has_plan_feature(subject: Union[object, None], feature: str) -> bool:
    """Evalúa si el usuario o compañía tiene acceso a la ``feature`` por plan."""

    company = None
    UserModel = get_user_model()

    if isinstance(subject, UserModel):
        company = subject.company
    else:
        company = subject

    plan_name = get_company_plan(company)
    required = PLAN_FEATURES.get(feature)

    if not required:
        return False

    return plan_satisfies(plan_name, required)


def build_menu_flags(role: str, plan_name: Optional[str]):
    """Información de utilidad para mostrar/ocultar módulos en templates."""

    return {
        "allow_reports": plan_satisfies(plan_name, "Estandar"),
        "allow_advanced_reports": plan_satisfies(plan_name, "Premium"),
        "branch_limit": get_branch_limit(plan_name),
        "role": role,
        "plan": plan_name or "Sin Plan",
    }
