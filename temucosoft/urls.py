from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView, RedirectView
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
    path('login/', TemplateView.as_view(template_name="login.html"), name='login'),
    path('dashboard/', TemplateView.as_view(template_name="dashboard.html"), name='dashboard'),
]