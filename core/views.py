from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import (
    Branch,
    Company,
    Inventory,
    Order,
    Product,
    Purchase,
    Sale,
    Subscription,
    Supplier,
    User,
)
from .permissions import IsAdminClienteOrGerente, IsSuperAdmin
from .serializers import (
    BranchSerializer,
    CompanySerializer,
    InventorySerializer,
    OrderSerializer,
    ProductSerializer,
    PurchaseSerializer,
    SaleSerializer,
    SubscriptionSerializer,
    SupplierSerializer,
    UserMeSerializer,
    UserSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'admin_cliente':
            return User.objects.filter(company=self.request.user.company)
        return super().get_queryset()

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data)


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @action(detail=True, methods=['post'], url_path='subscribe')
    def subscribe(self, request, pk=None):
        company = self.get_object()
        serializer = SubscriptionSerializer(data={**request.data, 'company': company.id})
        serializer.is_valid(raise_exception=True)
        subscription, _created = Subscription.objects.update_or_create(
            company=company,
            defaults=serializer.validated_data,
        )
        return Response(SubscriptionSerializer(subscription).data)


class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get_queryset(self):
        return Subscription.objects.all()

    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        subscription = self.get_object()
        company = subscription.company
        serializer = self.get_serializer(data={**request.data, 'company': company.id})
        serializer.is_valid(raise_exception=True)
        subscription, _created = Subscription.objects.update_or_create(
            company=company,
            defaults=serializer.validated_data,
        )
        output = SubscriptionSerializer(subscription)
        return Response(output.data)


class BranchViewSet(viewsets.ModelViewSet):
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated, IsAdminClienteOrGerente]

    def get_queryset(self):
        return Branch.objects.filter(company=self.request.user.company)

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.company:
            return Product.objects.filter(company=self.request.user.company)
        return Product.objects.all()

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)


class SupplierViewSet(viewsets.ModelViewSet):
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, IsAdminClienteOrGerente]

    def get_queryset(self):
        return Supplier.objects.filter(company=self.request.user.company)

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)


class InventoryViewSet(viewsets.ModelViewSet):
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Inventory.objects.filter(branch__company=self.request.user.company)
        branch_id = self.request.query_params.get('branch')
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        return queryset


class SaleViewSet(viewsets.ModelViewSet):
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Sale.objects.filter(branch__company=self.request.user.company)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PurchaseViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated, IsAdminClienteOrGerente]

    def get_queryset(self):
        return Purchase.objects.filter(branch__company=self.request.user.company)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.company:
            return Order.objects.filter(company=self.request.user.company)
        return Order.objects.none()

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)
