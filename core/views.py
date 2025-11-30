from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Product, Sale, Inventory, Branch, User
from .serializers import (
    ProductSerializer, SaleSerializer, InventorySerializer, 
    BranchSerializer, UserSerializer, UserMeSerializer
)
from .permissions import IsAdminClienteOrGerente

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Cada admin ve solo sus usuarios
        if self.request.user.role == 'admin_cliente':
            return User.objects.filter(company=self.request.user.company)
        return super().get_queryset()

    @action(detail=False, methods=['get'])
    def me(self, request):
        """ Endpoint clave para el Dashboard """
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data)

class BranchViewSet(viewsets.ModelViewSet):
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated, IsAdminClienteOrGerente]

    def get_queryset(self):
        return Branch.objects.filter(company=self.request.user.company)

    def perform_create(self, serializer):
        # Asigna la compañía automáticamente al crear
        serializer.save(company=self.request.user.company)

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(company=self.request.user.company)

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