from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Order, Product
import datetime

# Reutilizar las opciones del modelo Order
DELIVERY_TIME_CHOICES = [
    ('morning', 'Mañana (8:00 AM - 12:00 PM)'),
    ('afternoon', 'Tarde (12:00 PM - 6:00 PM)'),
    ('evening', 'Noche (6:00 PM - 9:00 PM)'),
]


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido'
        })
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Generar username automáticamente desde el email
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        # Generar username único desde el email
        base_username = self.cleaned_data['email'].split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        user.username = username
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'city', 'province']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '56835698',
                'required': True
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección completa',
                'rows': 3,
                'required': True
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ciudad',
                'required': True
            }),
            'province': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Provincia',
                'required': True
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer los campos requeridos en el formulario
        self.fields['phone'].required = True
        self.fields['address'].required = True
        self.fields['city'].required = True
        self.fields['province'].required = True
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        import re
        # Acepta: 8 dígitos solos, o +53 seguido de espacio opcional y 8 dígitos
        pattern = r'^(\d{8}|\+53\s?\d{8})$'
        if phone and not re.match(pattern, phone):
            raise forms.ValidationError("El número debe tener 8 dígitos (ejemplo: 56835698). El código +53 se agregará automáticamente.")
        # Si solo tiene 8 dígitos, agregar +53 automáticamente
        if phone and len(phone) == 8 and phone.isdigit():
            phone = f'+53 {phone}'
        return phone


class CheckoutForm(forms.ModelForm):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Efectivo al recibir'),
        ('transfer', 'Transferencia bancaria'),
    ]
    
    delivery_time = forms.ChoiceField(
        choices=DELIVERY_TIME_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )

    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = Order
        fields = ['delivery_address', 'delivery_city', 'delivery_province', 'contact_phone', 
                  'delivery_date', 'delivery_time', 'payment_method', 'notes']
        widgets = {
            'delivery_address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección completa de entrega',
                'rows': 3,
                'required': True
            }),
            'delivery_city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ciudad',
                'required': True
            }),
            'delivery_province': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Provincia',
                'required': True
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '56835698',
                'required': True
            }),
            'delivery_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': datetime.date.today().isoformat(),
                'required': True
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Notas adicionales (opcional)',
                'rows': 3
            }),
        }
    
    def clean_delivery_date(self):
        date = self.cleaned_data['delivery_date']
        if date < datetime.date.today():
            raise forms.ValidationError("La fecha de entrega no puede ser en el pasado")
        return date
    
    def clean_contact_phone(self):
        phone = self.cleaned_data['contact_phone']
        import re
        # Acepta: 8 dígitos solos, o +53 seguido de espacio opcional y 8 dígitos
        pattern = r'^(\d{8}|\+53\s?\d{8})$'
        if not re.match(pattern, phone):
            raise forms.ValidationError("El número debe tener 8 dígitos (ejemplo: 56835698). El código +53 se agregará automáticamente.")
        # Si solo tiene 8 dígitos, agregar +53 automáticamente
        if len(phone) == 8 and phone.isdigit():
            phone = f'+53 {phone}'
        return phone

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'category', 'name', 'sku', 'description', 'price', 
            'stock', 'image', 'featured', 'is_active'
        ]
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Martillo de Uña 16oz',
                'required': True
            }),
            'sku': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: FER-MAR-001',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción detallada del producto...',
                'rows': 4,
                'required': True
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01',
                'required': True
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0',
                'required': True
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'category': 'Categoría *',
            'name': 'Nombre del Producto *',
            'sku': 'SKU (Código Único) *',
            'description': 'Descripción *',
            'price': 'Precio *',
            'stock': 'Cantidad en Stock *',
            'image': 'Imagen del Producto',
            'featured': 'Producto Destacado',
            'is_active': 'Publicar Inmediatamente',
        }
    
    def clean_sku(self):
        """Validar que el SKU sea único"""
        sku = self.cleaned_data.get('sku')
        if sku:
            sku = sku.upper().strip()
            # Si estamos editando, excluir el producto actual
            if self.instance.pk:
                if Product.objects.exclude(pk=self.instance.pk).filter(sku=sku).exists():
                    raise forms.ValidationError('Este SKU ya existe. Debe ser único.')
            else:
                if Product.objects.filter(sku=sku).exists():
                    raise forms.ValidationError('Este SKU ya existe. Debe ser único.')
        return sku
    
    def clean_price(self):
        """Validar que el precio sea positivo"""
        price = self.cleaned_data.get('price')
        if price and price <= 0:
            raise forms.ValidationError('El precio debe ser mayor a 0')
        return price
    
    def clean_stock(self):
        """Validar que el stock no sea negativo"""
        stock = self.cleaned_data.get('stock')
        if stock and stock < 0:
            raise forms.ValidationError('El stock no puede ser negativo')
        return stock
    
    def clean_image(self):
        """Validar imagen"""
        image = self.cleaned_data.get('image')
        if image:
            # Validar tamaño (máximo 5MB)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError('La imagen no puede ser mayor a 5MB')
            
            # Validar tipo de archivo
            import os
            ext = os.path.splitext(image.name)[1].lower()
            valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
            if ext not in valid_extensions:
                raise forms.ValidationError(
                    f'Formato no válido. Use: {", ".join(valid_extensions)}'
                )
        
        return image
