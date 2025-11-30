from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core.views import (
    BranchViewSet,
    CompanyViewSet,
    InventoryViewSet,
    OrderViewSet,
    ProductViewSet,
    PurchaseViewSet,
    SaleViewSet,
    SubscriptionViewSet,
    SupplierViewSet,
    UserViewSet,
)
from core.web import (
    AdminClienteDashboardView,
    ClienteFinalDashboardView,
    ClientePlanDetailView,
    ClientePlanSelectionView,
    GerenteDashboardView,
    LogoutView,
    RoleLoginView,
    SuperAdminDashboardView,
    VendedorDashboardView,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'branches', BranchViewSet, basename='branch')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'inventory', InventoryViewSet, basename='inventory')
router.register(r'sales', SaleViewSet, basename='sale')
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'purchases', PurchaseViewSet, basename='purchase')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    # Redirección raíz a login
    path('', RedirectView.as_view(url='/login/', permanent=False)),
    
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    
    # JWT Auth
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Rutas Frontend
    path('login/', RoleLoginView.as_view(), name='login'),
    path('dashboard/super-admin/', SuperAdminDashboardView.as_view(), name='dashboard_super_admin'),
    path('dashboard/admin-cliente/', AdminClienteDashboardView.as_view(), name='dashboard_admin_cliente'),
    path('dashboard/gerente/', GerenteDashboardView.as_view(), name='dashboard_gerente'),
    path('dashboard/vendedor/', VendedorDashboardView.as_view(), name='dashboard_vendedor'),
    path('dashboard/cliente/', ClienteFinalDashboardView.as_view(), name='dashboard_cliente'),
    path('dashboard/cliente-final/', ClienteFinalDashboardView.as_view(), name='dashboard_cliente_final'),
    path('cliente/seleccionar-plan/', ClientePlanSelectionView.as_view(), name='cliente_plan_selection'),
    path('cliente/mi-plan/', ClientePlanDetailView.as_view(), name='cliente_plan_detail'),
    path('logout/', LogoutView.as_view(), name='logout'),
]