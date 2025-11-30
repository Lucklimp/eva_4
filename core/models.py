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
    """ Representa al cliente/tenant (La Pyme) """
    name = models.CharField(max_length=100)
    rut = models.CharField(max_length=12, validators=[validar_rut])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Subscription(models.Model):
    """ Controla qué plan tiene la empresa """
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
    """ Usuario personalizado """
    rut = models.CharField(max_length=12, validators=[validar_rut], blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLES, default='cliente_final')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    
    def clean(self):
        if self.role in ['admin_cliente', 'gerente', 'vendedor'] and not self.company:
            raise ValidationError("Este rol requiere estar asociado a una compañía.")

class Branch(models.Model):
    """ Sucursales (Validada por Plan) """
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)

    def clean(self):
        # REGLA DE NEGOCIO: Límites por Plan
        if not self.company_id:
            return

        # Buscamos la suscripción
        try:
            sub = Subscription.objects.get(company=self.company)
            # Contamos cuántas sucursales ya tiene (excluyendo la actual si se está editando)
            current_branches = Branch.objects.filter(company=self.company).exclude(pk=self.pk).count()

            if sub.plan_name == 'Basico' and current_branches >= 1:
                raise ValidationError("El Plan Básico permite máximo 1 sucursal.")
            
            if sub.plan_name == 'Estandar' and current_branches >= 3:
                raise ValidationError("El Plan Estándar permite máximo 3 sucursales.")
                
        except Subscription.DoesNotExist:
            pass # Si no hay suscripción, no aplicamos límite (o bloqueamos, según prefieras)

    def save(self, *args, **kwargs):
        self.full_clean() # Forzar validación antes de guardar
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    """ Producto con validación de SKU """
    sku_validator = RegexValidator(regex=r'^[A-Z]{3}-\d{4}$', message="Formato SKU inválido. Use AAA-0000")
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    sku = models.CharField(max_length=50, validators=[sku_validator]) 
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    cost = models.DecimalField(max_digits=10, decimal_places=0)
    
    def clean(self):
        if self.price < 0:
            raise ValidationError("El precio no puede ser negativo.")

class Inventory(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stock = models.IntegerField(default=0)
    
    def clean(self):
        if self.stock < 0:
            raise ValidationError("El stock no puede ser negativo.")

class Sale(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    total = models.DecimalField(max_digits=12, decimal_places=0)
    created_at = models.DateTimeField(default=timezone.now)

    def clean(self):
        if self.created_at > timezone.now():
            raise ValidationError("La venta no puede ser en el futuro.")

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=0)