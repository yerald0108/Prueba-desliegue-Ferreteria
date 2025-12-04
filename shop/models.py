from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, RegexValidator
from django.core.exceptions import ValidationError
from decimal import Decimal

def validate_phone_or_empty(value):
    """Validador que permite teléfono vacío o válido (formato cubano: 8 dígitos)"""
    if value:
        import re
        # Acepta: 8 dígitos solos, o +53 seguido de espacio opcional y 8 dígitos
        pattern = r'^(\d{8}|\+53\s?\d{8})$'
        if not re.match(pattern, value):
            raise ValidationError("El número debe tener 8 dígitos (ejemplo: 56835698). El código +53 se agregará automáticamente.")

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Categoría")
    name = models.CharField(max_length=200, verbose_name="Nombre")
    description = models.TextField(verbose_name="Descripción")
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name="Precio")
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name="Stock")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Imagen")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    featured = models.BooleanField(default=False, verbose_name="Destacado")
    sku = models.CharField(max_length=50, unique=True, verbose_name="SKU")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def in_stock(self):
        return self.stock > 0


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(validators=[validate_phone_or_empty], max_length=17, blank=True, default='', verbose_name="Teléfono")
    
    def save(self, *args, **kwargs):
        # Si el teléfono tiene solo 8 dígitos, agregar +53 automáticamente
        if self.phone:
            phone_clean = self.phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            if len(phone_clean) == 8 and phone_clean.isdigit():
                self.phone = f'+53 {phone_clean}'
            elif phone_clean.startswith('+53') and len(phone_clean) == 11:
                self.phone = f'+53 {phone_clean[3:]}'
        super().save(*args, **kwargs)
        
    address = models.TextField(blank=True, verbose_name="Dirección")
    city = models.CharField(max_length=100, blank=True, verbose_name="Ciudad")
    province = models.CharField(max_length=100, blank=True, verbose_name="Provincia")
    email_verified = models.BooleanField(default=False, verbose_name="Email verificado")
    verification_token = models.CharField(max_length=100, blank=True, null=True)
    verification_token_created = models.DateTimeField(null=True, blank=True)  # NUEVO: para expiración
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"
    
    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    def generate_verification_token(self):
        """Generar token de verificación único"""
        import uuid
        from django.utils import timezone
        
        self.verification_token = uuid.uuid4().hex
        self.verification_token_created = timezone.now()
        self.save()
        return self.verification_token
    
    def is_verification_token_valid(self):
        """Verificar si el token no ha expirado (24 horas)"""
        from django.utils import timezone
        from datetime import timedelta
        
        if not self.verification_token_created:
            return False
        
        expiration_time = self.verification_token_created + timedelta(hours=24)
        return timezone.now() < expiration_time


class Order(models.Model):
    PAYMENT_CHOICES = [
        ('cash', 'Efectivo'),
        ('transfer', 'Transferencia'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmado'),
        ('preparing', 'Preparando'),
        ('in_transit', 'En camino'),
        ('delivered', 'Entregado'),
        ('cancelled', 'Cancelado'),
    ]
    
    DELIVERY_TIME_CHOICES = [
        ('morning', 'Mañana (8:00 AM - 12:00 PM)'),
        ('afternoon', 'Tarde (12:00 PM - 6:00 PM)'),
        ('evening', 'Noche (6:00 PM - 9:00 PM)'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name="Usuario")
    order_number = models.CharField(max_length=20, unique=True, verbose_name="Número de orden")
    
    # Información de contacto y entrega
    delivery_address = models.TextField(verbose_name="Dirección de entrega")
    delivery_city = models.CharField(max_length=100, verbose_name="Ciudad")
    delivery_province = models.CharField(max_length=100, verbose_name="Provincia")
    contact_phone = models.CharField(max_length=17, verbose_name="Teléfono de contacto")
    delivery_date = models.DateField(verbose_name="Fecha de entrega")
    delivery_time = models.CharField(max_length=50, choices=DELIVERY_TIME_CHOICES, verbose_name="Hora de entrega")
    
    # Información de pago y estado
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, verbose_name="Método de pago")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Estado")
    
    # Totales
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal")
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Costo de envío")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total")
    
    # Notas
    notes = models.TextField(blank=True, verbose_name="Notas adicionales")
    admin_notes = models.TextField(blank=True, verbose_name="Notas del administrador")
    cancellation_reason = models.TextField(blank=True, verbose_name="Motivo de cancelación")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    
    class Meta:
        verbose_name = "Orden"
        verbose_name_plural = "Órdenes"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Orden {self.order_number} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Orden")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Producto")
    quantity = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="Cantidad")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio unitario")
    
    class Meta:
        verbose_name = "Item de Orden"
        verbose_name_plural = "Items de Orden"
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
    
    @property
    def subtotal(self):
        return self.quantity * self.price


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', verbose_name="Usuario")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Carrito"
        verbose_name_plural = "Carritos"
    
    def __str__(self):
        return f"Carrito de {self.user.username}"
    
    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())
    
    @property
    def items_count(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name="Carrito")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Producto")
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)], verbose_name="Cantidad")
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Item del Carrito"
        verbose_name_plural = "Items del Carrito"
        unique_together = ['cart', 'product']
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
    
    @property
    def subtotal(self):
        return self.quantity * self.product.price
