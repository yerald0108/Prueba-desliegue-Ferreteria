"""
Script para poblar productos con características completas.
Ejecutar desde Django shell: python manage.py shell < populate_products.py
"""

from shop.models import Product, Category
from decimal import Decimal

def populate_products_with_specs():
    """Agregar especificaciones a productos existentes o crear nuevos"""
    
    # Obtener o crear categoría de Herramientas Eléctricas
    cat_electric, _ = Category.objects.get_or_create(
        slug='herramientas-electricas',
        defaults={
            'name': 'Herramientas Eléctricas',
            'description': 'Taladros, sierras y más'
        }
    )
    
    # Obtener o crear categoría de Herramientas Manuales
    cat_manual, _ = Category.objects.get_or_create(
        slug='herramientas-manuales',
        defaults={
            'name': 'Herramientas Manuales',
            'description': 'Martillos, llaves y más'
        }
    )
    
    # =====================================================
    # PRODUCTO 1: Taladro Eléctrico Profesional
    # =====================================================
    taladro, created = Product.objects.update_or_create(
        sku='HE-TAL-001',
        defaults={
            'category': cat_electric,
            'name': 'Taladro Eléctrico Profesional 800W',
            'description': 'Taladro de impacto profesional con regulador de velocidad y reverse. Ideal para trabajos pesados en concreto, metal y madera.',
            'price': Decimal('89.99'),
            'stock': 15,
            'is_active': True,
            'featured': True,
            
            # Especificaciones Físicas
            'material': 'Carcasa de plástico ABS reforzado',
            'dimensiones': '28cm x 8cm x 22cm',
            'peso': Decimal('2.5'),
            'color': 'Azul y Negro',
            
            # Especificaciones Técnicas
            'voltaje': '110V',
            'potencia': '800W',
            
            # Información Comercial
            'marca': 'DeWalt',
            'garantia': '2 años',
            'uso_recomendado': 'Perforación en concreto, metal, madera y plástico. Ideal para uso profesional en construcción.',
        }
    )
    print(f"{'✅ Creado' if created else '🔄 Actualizado'}: {taladro.name}")
    
    # =====================================================
    # PRODUCTO 2: Sierra Circular
    # =====================================================
    sierra, created = Product.objects.update_or_create(
        sku='HE-SIE-001',
        defaults={
            'category': cat_electric,
            'name': 'Sierra Circular 1500W con Láser',
            'description': 'Sierra circular de alta potencia con guía láser para cortes precisos. Incluye hoja de 7.25 pulgadas y protector de seguridad.',
            'price': Decimal('125.50'),
            'stock': 8,
            'is_active': True,
            'featured': True,
            
            # Especificaciones Físicas
            'material': 'Aluminio fundido y acero',
            'dimensiones': '35cm x 25cm x 25cm',
            'peso': Decimal('4.2'),
            'color': 'Naranja y Negro',
            
            # Especificaciones Técnicas
            'voltaje': '110V',
            'potencia': '1500W',
            
            # Información Comercial
            'marca': 'Makita',
            'garantia': '3 años',
            'uso_recomendado': 'Corte de madera, plástico y materiales compuestos. Para carpintería profesional.',
        }
    )
    print(f"{'✅ Creado' if created else '🔄 Actualizado'}: {sierra.name}")
    
    # =====================================================
    # PRODUCTO 3: Martillo de Uña
    # =====================================================
    martillo, created = Product.objects.update_or_create(
        sku='HM-MAR-001',
        defaults={
            'category': cat_manual,
            'name': 'Martillo de Uña 16oz Mango Fibra',
            'description': 'Martillo profesional con cabeza forjada en acero de alta resistencia. Mango ergonómico de fibra de vidrio con grip antideslizante.',
            'price': Decimal('24.99'),
            'stock': 45,
            'is_active': True,
            'featured': False,
            
            # Especificaciones Físicas
            'material': 'Cabeza de acero forjado, mango de fibra de vidrio',
            'dimensiones': '33cm de largo',
            'peso': Decimal('0.45'),
            'color': 'Rojo y Negro',
            
            # Especificaciones Técnicas (N/A para herramientas manuales)
            'voltaje': '',
            'potencia': '',
            
            # Información Comercial
            'marca': 'Stanley',
            'garantia': 'Garantía de por vida',
            'uso_recomendado': 'Clavado y extracción de clavos. Uso general en construcción y carpintería.',
        }
    )
    print(f"{'✅ Creado' if created else '🔄 Actualizado'}: {martillo.name}")
    
    # =====================================================
    # PRODUCTO 4: Amoladora Angular
    # =====================================================
    amoladora, created = Product.objects.update_or_create(
        sku='HE-AMO-001',
        defaults={
            'category': cat_electric,
            'name': 'Amoladora Angular 900W 4.5 pulgadas',
            'description': 'Amoladora angular profesional con protector ajustable y empuñadura lateral. Perfecta para corte y desbaste de metal.',
            'price': Decimal('67.00'),
            'stock': 12,
            'is_active': True,
            'featured': True,
            
            # Especificaciones Físicas
            'material': 'Carcasa metálica con recubrimiento plástico',
            'dimensiones': '30cm x 10cm x 15cm',
            'peso': Decimal('2.1'),
            'color': 'Verde y Negro',
            
            # Especificaciones Técnicas
            'voltaje': '110V',
            'potencia': '900W',
            
            # Información Comercial
            'marca': 'Bosch',
            'garantia': '1 año',
            'uso_recomendado': 'Corte y desbaste de metal, concreto y piedra. Para uso industrial y profesional.',
        }
    )
    print(f"{'✅ Creado' if created else '🔄 Actualizado'}: {amoladora.name}")
    
    print("\n" + "="*60)
    print("✅ ¡Productos poblados exitosamente!")
    print("="*60)
    print(f"\nAhora puedes:")
    print(f"1. Ir a /productos/")
    print(f"2. Seleccionar estos productos con los checkboxes de comparación")
    print(f"3. Hacer clic en 'Ver Comparación'")
    print(f"4. ¡Verás todas las especificaciones llenas!")
    print("\n" + "="*60)

# Ejecutar
if __name__ == "__main__":
    populate_products_with_specs()