# shop/admin.py
from django.contrib import admin
from .models import (
    Category, Product, Order, OrderItem, 
    Cart, CartItem, UserProfile, Review, 
    ReviewHelpful, Wishlist, WishlistItem
)

# ==========================================
# ADMIN PARA PRODUCT CON ESPECIFICACIONES
# ==========================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'sku', 'name', 'category', 'price', 'stock', 
        'marca', 'is_active', 'featured', 'created_at'
    ]
    
    list_filter = [
        'is_active', 'featured', 'category', 'marca', 'created_at'
    ]
    
    search_fields = [
        'name', 'sku', 'description', 'marca', 'material'
    ]
    
    prepopulated_fields = {'sku': ('name',)}  # Auto-generar SKU desde nombre
    
    # ==========================================
    # ORGANIZACIÓN EN FIELDSETS
    # ==========================================
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'sku', 'category', 'description', 'image')
        }),
        
        ('Especificaciones Físicas', {
            'fields': ('material', 'dimensiones', 'peso', 'color'),
            'classes': ('collapse',),  # Colapsable por defecto
            'description': 'Características físicas del producto'
        }),
        
        ('Especificaciones Técnicas', {
            'fields': ('voltaje', 'potencia'),
            'classes': ('collapse',),
            'description': 'Para productos eléctricos o mecánicos'
        }),
        
        ('Información Comercial', {
            'fields': ('marca', 'garantia', 'price', 'stock', 'uso_recomendado')
        }),
        
        ('Estado y Visibilidad', {
            'fields': ('is_active', 'featured'),
            'description': 'Control de publicación del producto'
        }),
    )
    
    # ==========================================
    # ACCIONES PERSONALIZADAS
    # ==========================================
    actions = ['activar_productos', 'desactivar_productos', 'marcar_destacados']
    
    def activar_productos(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} producto(s) activado(s).')
    activar_productos.short_description = "✅ Activar productos seleccionados"
    
    def desactivar_productos(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} producto(s) desactivado(s).')
    desactivar_productos.short_description = "❌ Desactivar productos seleccionados"
    
    def marcar_destacados(self, request, queryset):
        updated = queryset.update(featured=True)
        self.message_user(request, f'{updated} producto(s) marcado(s) como destacados.')
    marcar_destacados.short_description = "⭐ Marcar como destacados"
    
    # ==========================================
    # OPTIMIZACIONES
    # ==========================================
    list_select_related = ['category']  # Evitar N+1 queries
    
    readonly_fields = ['created_at', 'updated_at']
    
    # Mostrar fechas en el detalle
    fieldsets += (
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


# ==========================================
# ADMIN PARA OTROS MODELOS (BÁSICO)
# ==========================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'user', 'status', 'total', 
        'payment_method', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'user__username', 'user__email']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Información de la Orden', {
            'fields': ('order_number', 'user', 'status', 'payment_method')
        }),
        ('Entrega', {
            'fields': (
                'delivery_address', 'delivery_city', 'delivery_province',
                'contact_phone', 'delivery_date', 'delivery_time'
            )
        }),
        ('Totales', {
            'fields': ('subtotal', 'delivery_fee', 'total')
        }),
        ('Notas', {
            'fields': ('notes', 'admin_notes', 'cancellation_reason'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']
    list_filter = ['order__status']
    search_fields = ['order__order_number', 'product__name']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'email_verified']
    list_filter = ['email_verified', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    readonly_fields = ['verification_token_created', 'created_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'user', 'rating', 'is_verified_purchase', 
        'is_approved', 'created_at'
    ]
    list_filter = ['rating', 'is_verified_purchase', 'is_approved', 'created_at']
    search_fields = ['product__name', 'user__username', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['aprobar_reviews', 'rechazar_reviews']
    
    def aprobar_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} review(s) aprobado(s).')
    aprobar_reviews.short_description = "✅ Aprobar reviews"
    
    def rechazar_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} review(s) rechazado(s).')
    rechazar_reviews.short_description = "❌ Rechazar reviews"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'added_at']
    search_fields = ['cart__user__username', 'product__name']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']
    search_fields = ['user__username']


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ['wishlist', 'product', 'added_at']
    search_fields = ['wishlist__user__username', 'product__name']


# Ocultar ReviewHelpful del admin (tabla técnica)
# admin.site.register(ReviewHelpful)