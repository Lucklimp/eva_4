"""Utilidades comunes para manejo de planes y helpers de vistas."""

from typing import Dict, List, Optional, Union

from django.contrib.auth import get_user_model


PLAN_ORDER = ["Basico", "Estandar", "Premium"]

# Definición centralizada de features asociadas a planes.
PLAN_FEATURES = {
    "basic_features": "Basico",
    "standard_reports": "Estandar",
    "advanced_reports": "Premium",
    "unlimited_branches": "Premium",
}

PLAN_LIMITS: Dict[str, Optional[int]] = {"Basico": 1, "Estandar": 3, "Premium": None}

PLAN_CATALOG: Dict[str, Dict[str, Union[str, List[str]]]] = {
    "Basico": {
        "label": "Básico",
        "benefits": [
            "Acceso a funciones esenciales",
            "Máximo 1 sucursal",
            "Reportes avanzados ocultos",
        ],
    },
    "Estandar": {
        "label": "Estándar",
        "benefits": [
            "Hasta 3 sucursales",
            "Reportes estándar incluidos",
            "Opción de crecer a Premium",
        ],
    },
    "Premium": {
        "label": "Premium",
        "benefits": [
            "Sucursales ilimitadas",
            "Reportes avanzados",
            "Todas las funcionalidades disponibles",
        ],
    },
}


def plan_satisfies(plan_name: Optional[str], required: str) -> bool:
    """Indica si ``plan_name`` cumple con el plan mínimo requerido."""

    if not plan_name or plan_name not in PLAN_ORDER:
        return False

    try:
        return PLAN_ORDER.index(plan_name) >= PLAN_ORDER.index(required)
    except ValueError:
        return False


def get_plan_catalog_items():
    """Retorna los planes ordenados con sus etiquetas y beneficios."""

    ordered = []
    for name in PLAN_ORDER:
        data = PLAN_CATALOG.get(name, {})
        ordered.append({"value": name, "label": data.get("label", name), "benefits": data.get("benefits", [])})
    return ordered


def get_company_plan(company) -> Optional[str]:
    """Obtiene el nombre del plan de la compañía si existe."""

    if not company:
        return None

    subscription = getattr(company, "subscription", None)
    if subscription and subscription.active:
        return subscription.plan_name
    return None


def has_feature(subject: Union[object, str, None], feature: str) -> bool:
    """Evalúa si el usuario, compañía o nombre de plan tiene acceso a la ``feature``."""

    company = None
    plan_name = subject if isinstance(subject, str) else None
    UserModel = get_user_model()

    if plan_name is None:
        if isinstance(subject, UserModel):
            company = subject.company
        else:
            company = subject
        plan_name = get_company_plan(company)

    required = PLAN_FEATURES.get(feature)

    if not required:
        return False

    return plan_satisfies(plan_name, required)


def get_branch_limit(subject: Union[object, str, None]) -> Optional[int]:
    """Retorna el límite de sucursales según el plan (``None`` significa ilimitado)."""

    if has_feature(subject, "unlimited_branches"):
        return None

    if isinstance(subject, str):
        plan_name = subject
    else:
        plan_name = get_company_plan(subject.company if hasattr(subject, "company") else subject)

    return PLAN_LIMITS.get(plan_name)


def build_menu_flags(user) -> Dict[str, Union[str, Optional[int], bool]]:
    """Información de utilidad para mostrar/ocultar módulos en templates."""

    plan_name = get_company_plan(user.company) if user.is_authenticated else None
    return {
        "has_standard_reports": has_feature(user, "standard_reports"),
        "has_advanced_reports": has_feature(user, "advanced_reports"),
        "branch_limit": get_branch_limit(user),
        "role": user.role,
        "plan": plan_name or "Sin Plan",
    }
