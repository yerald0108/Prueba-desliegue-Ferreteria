"""
Script para poblar la base de datos con datos de ejemplo
Ejecutar con: python manage.py shell < populate_db.py
"""

from shop.models import Category, Product
from django.contrib.auth.models import User
from decimal import Decimal

print("🚀 Iniciando población de base de datos...")

# Crear categorías
print("\n📁 Creando categorías...")
categories_data = [
    {
        'name': 'Ferretería',
        'slug': 'ferreteria',
        'description': 'Herramientas y materiales de ferretería'
    },
    {
        'name': 'Miscelánea',
        'slug': 'miscelanea',
        'description': 'Artículos varios para el hogar'
    },
    {
        'name': 'Herramientas',
        'slug': 'herramientas',
        'description': 'Herramientas manuales y eléctricas'
    },
    {
        'name': 'Pinturas',
        'slug': 'pinturas',
        'description': 'Pinturas y accesorios para pintar'
    },
    {
        'name': 'Electricidad',
        'slug': 'electricidad',
        'description': 'Material eléctrico y cables'
    },
    {
        'name': 'Plomería',
        'slug': 'plomeria',
        'description': 'Accesorios y materiales de plomería'
    }
]

categories = {}
for cat_data in categories_data:
    cat, created = Category.objects.get_or_create(
        slug=cat_data['slug'],
        defaults={
            'name': cat_data['name'],
            'description': cat_data['description']
        }
    )
    categories[cat_data['slug']] = cat
    status = "✅ Creada" if created else "⏭️  Ya existe"
    print(f"  {status}: {cat.name}")

# Crear productos de ejemplo
print("\n🛒 Creando productos...")
products_data = [
    # Ferretería
    {
        'category': 'ferreteria',
        'name': 'Martillo de Uña 16oz',
        'sku': 'FER-MAR-001',
        'description': 'Martillo profesional de uña con mango ergonómico de fibra de vidrio. Ideal para trabajos de construcción y carpintería.',
        'price': Decimal('15.99'),
        'stock': 45,
        'featured': True
    },
    {
        'category': 'ferreteria',
        'name': 'Clavos de Acero 2" (500g)',
        'sku': 'FER-CLA-002',
        'description': 'Clavos de acero galvanizado de 2 pulgadas, paquete de 500 gramos. Ideales para carpintería general.',
        'price': Decimal('4.50'),
        'stock': 150,
        'featured': False
    },
    {
        'category': 'ferreteria',
        'name': 'Tornillos para Madera 100 pcs',
        'sku': 'FER-TOR-003',
        'description': 'Caja de 100 tornillos para madera de diferentes medidas. Acabado galvanizado.',
        'price': Decimal('8.75'),
        'stock': 80,
        'featured': False
    },
    
    # Herramientas
    {
        'category': 'herramientas',
        'name': 'Destornillador Set 6 Piezas',
        'sku': 'HER-DES-001',
        'description': 'Set de 6 destornilladores con puntas Phillips y planas. Mangos ergonómicos con grip antideslizante.',
        'price': Decimal('12.99'),
        'stock': 60,
        'featured': True
    },
    {
        'category': 'herramientas',
        'name': 'Llave Inglesa Ajustable 10"',
        'sku': 'HER-LLA-002',
        'description': 'Llave inglesa ajustable de 10 pulgadas. Acabado cromado, apertura máxima de 28mm.',
        'price': Decimal('18.50'),
        'stock': 35,
        'featured': True
    },
    {
        'category': 'herramientas',
        'name': 'Alicate Universal 8"',
        'sku': 'HER-ALI-003',
        'description': 'Alicate universal de 8 pulgadas con mangos aislados. Ideal para trabajos eléctricos.',
        'price': Decimal('14.25'),
        'stock': 50,
        'featured': False
    },
    {
        'category': 'herramientas',
        'name': 'Sierra Manual para Madera',
        'sku': 'HER-SIE-004',
        'description': 'Sierra manual con hoja de acero templado. Mango ergonómico de plástico.',
        'price': Decimal('22.00'),
        'stock': 25,
        'featured': False
    },
    
    # Pinturas
    {
        'category': 'pinturas',
        'name': 'Pintura Látex Blanca 1 Galón',
        'sku': 'PIN-LAT-001',
        'description': 'Pintura látex interior/exterior color blanco. Rendimiento aproximado: 10-12 m² por galón.',
        'price': Decimal('25.99'),
        'stock': 40,
        'featured': True
    },
    {
        'category': 'pinturas',
        'name': 'Brocha 3 Pulgadas',
        'sku': 'PIN-BRO-002',
        'description': 'Brocha profesional de 3 pulgadas con cerdas sintéticas. Mango de madera barnizada.',
        'price': Decimal('6.50'),
        'stock': 90,
        'featured': False
    },
    {
        'category': 'pinturas',
        'name': 'Rodillo con Extensión',
        'sku': 'PIN-ROD-003',
        'description': 'Rodillo de 9 pulgadas con extensión telescópica. Incluye 2 recambios.',
        'price': Decimal('16.75'),
        'stock': 45,
        'featured': False
    },
    {
        'category': 'pinturas',
        'name': 'Cinta de Pintor 2"',
        'sku': 'PIN-CIN-004',
        'description': 'Cinta adhesiva de baja adherencia para pintar. Rollo de 50 metros.',
        'price': Decimal('4.99'),
        'stock': 120,
        'featured': False
    },
    
    # Electricidad
    {
        'category': 'electricidad',
        'name': 'Cable Eléctrico 2x14 (10m)',
        'sku': 'ELE-CAB-001',
        'description': 'Cable eléctrico calibre 14 AWG, 2 hilos. Rollo de 10 metros. Certificado.',
        'price': Decimal('18.50'),
        'stock': 55,
        'featured': True
    },
    {
        'category': 'electricidad',
        'name': 'Bombillo LED 9W Luz Blanca',
        'sku': 'ELE-BOM-002',
        'description': 'Bombillo LED de 9W equivalente a 60W incandescente. Luz blanca fría, base E27.',
        'price': Decimal('5.99'),
        'stock': 200,
        'featured': True
    },
    {
        'category': 'electricidad',
        'name': 'Interruptor Simple',
        'sku': 'ELE-INT-003',
        'description': 'Interruptor simple de pared, color blanco. 15A, 120V.',
        'price': Decimal('3.25'),
        'stock': 150,
        'featured': False
    },
    {
        'category': 'electricidad',
        'name': 'Tomacorriente Doble',
        'sku': 'ELE-TOM-004',
        'description': 'Tomacorriente doble polarizado, color blanco. 15A, 120V.',
        'price': Decimal('4.50'),
        'stock': 140,
        'featured': False
    },
    
    # Plomería
    {
        'category': 'plomeria',
        'name': 'Codo PVC 1/2" 90°',
        'sku': 'PLO-COD-001',
        'description': 'Codo de PVC de 1/2 pulgada a 90 grados. Material resistente y duradero.',
        'price': Decimal('0.85'),
        'stock': 300,
        'featured': False
    },
    {
        'category': 'plomeria',
        'name': 'Tubo PVC 1/2" (3m)',
        'sku': 'PLO-TUB-002',
        'description': 'Tubo de PVC de 1/2 pulgada, longitud 3 metros. Presión 315 PSI.',
        'price': Decimal('6.75'),
        'stock': 75,
        'featured': False
    },
    {
        'category': 'plomeria',
        'name': 'Llave de Paso 1/2"',
        'sku': 'PLO-LLA-003',
        'description': 'Llave de paso de bola de 1/2 pulgada. Acabado cromado.',
        'price': Decimal('12.50'),
        'stock': 40,
        'featured': False
    },
    
    # Miscelánea
    {
        'category': 'miscelanea',
        'name': 'Escoba de Plástico',
        'sku': 'MIS-ESC-001',
        'description': 'Escoba de cerdas plásticas resistentes. Mango de metal con rosca estándar.',
        'price': Decimal('8.99'),
        'stock': 65,
        'featured': False
    },
    {
        'category': 'miscelanea',
        'name': 'Recogedor de Metal',
        'sku': 'MIS-REC-002',
        'description': 'Recogedor de metal galvanizado con mango largo. Durabilidad garantizada.',
        'price': Decimal('5.75'),
        'stock': 70,
        'featured': False
    },
    {
        'category': 'miscelanea',
        'name': 'Balde Plástico 10L',
        'sku': 'MIS-BAL-003',
        'description': 'Balde de plástico resistente de 10 litros con asa metálica.',
        'price': Decimal('7.50'),
        'stock': 50,
        'featured': False
    },
    {
        'category': 'miscelanea',
        'name': 'Candado de Seguridad 40mm',
        'sku': 'MIS-CAN-004',
        'description': 'Candado de seguridad con arco de 40mm. Incluye 3 llaves.',
        'price': Decimal('11.99'),
        'stock': 45,
        'featured': True
    }
]

for prod_data in products_data:
    category = categories[prod_data['category']]
    prod, created = Product.objects.get_or_create(
        sku=prod_data['sku'],
        defaults={
            'category': category,
            'name': prod_data['name'],
            'description': prod_data['description'],
            'price': prod_data['price'],
            'stock': prod_data['stock'],
            'featured': prod_data['featured'],
            'is_active': True
        }
    )
    status = "✅ Creado" if created else "⏭️  Ya existe"
    featured = "⭐" if prod.featured else ""
    print(f"  {status}: {prod.name} {featured} - ${prod.price} ({prod.stock} unidades)")

print("\n" + "="*60)
print("✅ Base de datos poblada exitosamente!")
print("="*60)
print("\n📊 Resumen:")
print(f"   Categorías: {Category.objects.count()}")
print(f"   Productos: {Product.objects.count()}")
print(f"   Productos destacados: {Product.objects.filter(featured=True).count()}")
print("\n🎉 ¡Tu tienda está lista para empezar a vender!")
print("\n💡 Consejos:")
print("   1. Accede al admin en /admin/ para ver todos los productos")
print("   2. Crea un usuario de prueba en /registro/")
print("   3. Agrega imágenes a los productos desde el admin")
print("   4. Prueba el flujo completo de compra")
print("\n🚀 Inicia el servidor con: python manage.py runserver\n")