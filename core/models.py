from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from .validators import validar_rut

# Roles definidos
ROLES = (
    ('super_admin', 'Super Admin'),
    ('admin_cliente', 'Admin Cliente'),
    ('gerente', 'Gerente'),
    ('vendedor', 'Vendedor'),
    ('cliente_final', 'Cliente Final'),
)

# Planes de suscripción
PLANES = (
    ('Basico', 'Básico'),      # 1 Sucursal, Sin reportes
    ('Estandar', 'Estándar'),  # 3 Sucursales, Con reportes
    ('Premium', 'Premium')     # Ilimitado
)


class Company(models.Model):
    """Representa al cliente/tenant (La Pyme)."""

    name = models.CharField(max_length=100)
    rut = models.CharField(max_length=12, validators=[validar_rut])
    address = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    """Controla qué plan tiene la empresa."""

    company = models.OneToOneField(Company, on_delete=models.CASCADE)
    plan_name = models.CharField(max_length=20, choices=PLANES, default='Basico')
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=True)

    def clean(self):
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValidationError("La fecha de fin debe ser posterior a la de inicio.")

    def __str__(self):
        return f"{self.company.name} - {self.plan_name}"


class User(AbstractUser):
    """Usuario personalizado."""

    rut = models.CharField(max_length=12, validators=[validar_rut], blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLES, default='cliente_final')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.role in ['admin_cliente', 'gerente', 'vendedor'] and not self.company:
            raise ValidationError("Este rol requiere estar asociado a una compañía.")


class Branch(models.Model):
    """Sucursales (validadas por el plan)."""

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)

    def clean(self):
        # Regla de negocio: Límites por plan
        if not self.company_id:
            return

        try:
            sub = Subscription.objects.get(company=self.company)
            current_branches = Branch.objects.filter(company=self.company).exclude(pk=self.pk).count()

            from .utils import get_branch_limit

            branch_limit = get_branch_limit(sub.plan_name)
            if branch_limit is not None and current_branches >= branch_limit:
                raise ValidationError(
                    f"El Plan {sub.plan_name} permite máximo {branch_limit} sucursal(es)."
                )
        except Subscription.DoesNotExist:
            # Si no hay suscripción registrada, no aplicamos límite (o podríamos bloquear)
            pass

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    """Producto con validación de SKU."""

    sku_validator = RegexValidator(regex=r'^[A-Z]{3}-\d{4}$', message="Formato SKU inválido. Use AAA-0000")

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    sku = models.CharField(max_length=50, validators=[sku_validator])
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    cost = models.DecimalField(max_digits=10, decimal_places=0)
    category = models.CharField(max_length=100, blank=True)

    def clean(self):
        if self.price < 0:
            raise ValidationError("El precio no puede ser negativo.")
        if self.cost < 0:
            raise ValidationError("El costo no puede ser negativo.")

    def __str__(self):
        return f"{self.sku} - {self.name}"


class Inventory(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stock = models.IntegerField(default=0)
    reorder_point = models.PositiveIntegerField(default=0)

    def clean(self):
        if self.stock < 0:
            raise ValidationError("El stock no puede ser negativo.")

    class Meta:
        unique_together = ('branch', 'product')

    def __str__(self):
        return f"{self.branch.name} - {self.product.sku}: {self.stock}"


class Supplier(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    rut = models.CharField(max_length=12, validators=[validar_rut])
    contact = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return self.name


class Purchase(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    total = models.DecimalField(max_digits=12, decimal_places=0)
    date = models.DateField(default=timezone.localdate)

    def clean(self):
        if self.date and self.date > timezone.localdate():
            raise ValidationError("La fecha de compra no puede estar en el futuro.")

    def __str__(self):
        return f"Compra {self.id} - {self.supplier.name}"


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=0)

    def clean(self):
        if self.quantity < 1:
            raise ValidationError("La cantidad debe ser al menos 1.")
        if self.price < 0:
            raise ValidationError("El precio no puede ser negativo.")

    def __str__(self):
        return f"{self.product.sku} x {self.quantity}"


class Sale(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    total = models.DecimalField(max_digits=12, decimal_places=0)
    created_at = models.DateTimeField(default=timezone.now)

    def clean(self):
        if self.created_at > timezone.now():
            raise ValidationError("La venta no puede ser en el futuro.")

    def __str__(self):
        return f"Venta {self.id} - {self.branch.name}"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=0)

    def clean(self):
        if self.quantity < 1:
            raise ValidationError("La cantidad debe ser al menos 1.")
        if self.price < 0:
            raise ValidationError("El precio no puede ser negativo.")

    def __str__(self):
        return f"{self.product.sku} x {self.quantity}"


ORDER_STATES = (
    ('pendiente', 'Pendiente'),
    ('enviado', 'Enviado'),
    ('entregado', 'Entregado'),
)


class Order(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField()
    status = models.CharField(max_length=20, choices=ORDER_STATES, default='pendiente')
    total = models.DecimalField(max_digits=12, decimal_places=0)
    created_at = models.DateTimeField(default=timezone.now)

    def clean(self):
        if self.created_at > timezone.now():
            raise ValidationError("La orden no puede tener fecha futura.")

    def __str__(self):
        return f"Orden {self.id} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=0)

    def clean(self):
        if self.quantity < 1:
            raise ValidationError("La cantidad debe ser al menos 1.")
        if self.price < 0:
            raise ValidationError("El precio no puede ser negativo.")

    def __str__(self):
        return f"{self.product.sku} x {self.quantity}"
