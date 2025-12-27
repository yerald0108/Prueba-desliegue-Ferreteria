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
    },
    {
        'name': 'Herramientas Eléctricas',
        'slug': 'herramientas-electricas',
        'description': 'Taladros, sierras y más'
    },
    {
        'name': 'Herramientas Manuales',
        'slug': 'herramientas-manuales',
        'description': 'Martillos, llaves y más'
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
        'featured': True,
        # Especificaciones Físicas
        'material': 'Cabeza de acero forjado, mango de fibra de vidrio',
        'dimensiones': '33cm de largo',
        'peso': Decimal('0.45'),
        'color': 'Rojo y Negro',
        # Especificaciones Técnicas
        'voltaje': '',
        'potencia': '',
        # Información Comercial
        'marca': 'Stanley',
        'garantia': 'Garantía de por vida',
        'uso_recomendado': 'Clavado y extracción de clavos. Uso general en construcción y carpintería.',
    },
    {
        'category': 'ferreteria',
        'name': 'Clavos de Acero 2" (500g)',
        'sku': 'FER-CLA-002',
        'description': 'Clavos de acero galvanizado de 2 pulgadas, paquete de 500 gramos. Ideales para carpintería general.',
        'price': Decimal('4.50'),
        'stock': 150,
        'featured': False,
        'material': 'Acero galvanizado',
        'dimensiones': '5cm x 5cm x 10cm (paquete)',
        'peso': Decimal('0.5'),
        'color': 'Plateado',
        'voltaje': '',
        'potencia': '',
        'marca': 'Generico',
        'garantia': 'N/A',
        'uso_recomendado': 'Para clavado en madera en trabajos de carpintería general.',
    },
    {
        'category': 'ferreteria',
        'name': 'Tornillos para Madera 100 pcs',
        'sku': 'FER-TOR-003',
        'description': 'Caja de 100 tornillos para madera de diferentes medidas. Acabado galvanizado.',
        'price': Decimal('8.75'),
        'stock': 80,
        'featured': False,
        'material': 'Acero galvanizado',
        'dimensiones': '8cm x 8cm x 3cm (caja)',
        'peso': Decimal('0.35'),
        'color': 'Plateado',
        'voltaje': '',
        'potencia': '',
        'marca': 'Generico',
        'garantia': 'N/A',
        'uso_recomendado': 'Para fijación en madera, muebles y estructuras de madera.',
    },
    
    # Herramientas Manuales
    {
        'category': 'herramientas-manuales',
        'name': 'Destornillador Set 6 Piezas',
        'sku': 'HER-DES-001',
        'description': 'Set de 6 destornilladores con puntas Phillips y planas. Mangos ergonómicos con grip antideslizante.',
        'price': Decimal('12.99'),
        'stock': 60,
        'featured': True,
        'material': 'Puntas de acero cromado, mangos de plástico',
        'dimensiones': '25cm x 15cm x 3cm (estuche)',
        'peso': Decimal('0.8'),
        'color': 'Rojo y Negro',
        'voltaje': '',
        'potencia': '',
        'marca': 'Stanley',
        'garantia': '1 año',
        'uso_recomendado': 'Para trabajos de electricidad, electrónica y reparaciones generales.',
    },
    {
        'category': 'herramientas-manuales',
        'name': 'Llave Inglesa Ajustable 10"',
        'sku': 'HER-LLA-002',
        'description': 'Llave inglesa ajustable de 10 pulgadas. Acabado cromado, apertura máxima de 28mm.',
        'price': Decimal('18.50'),
        'stock': 35,
        'featured': True,
        'material': 'Acero cromado',
        'dimensiones': '25cm de largo',
        'peso': Decimal('0.65'),
        'color': 'Plateado',
        'voltaje': '',
        'potencia': '',
        'marca': 'Bahco',
        'garantia': '5 años',
        'uso_recomendado': 'Para apriete y ajuste de tuercas y pernos de diferentes medidas.',
    },
    {
        'category': 'herramientas-manuales',
        'name': 'Alicate Universal 8"',
        'sku': 'HER-ALI-003',
        'description': 'Alicate universal de 8 pulgadas con mangos aislados. Ideal para trabajos eléctricos.',
        'price': Decimal('14.25'),
        'stock': 50,
        'featured': False,
        'material': 'Acero templado, mangos aislados',
        'dimensiones': '20cm de largo',
        'peso': Decimal('0.3'),
        'color': 'Naranja y Negro',
        'voltaje': '',
        'potencia': '',
        'marca': 'Knipex',
        'garantia': '2 años',
        'uso_recomendado': 'Para trabajos eléctricos, corte de cables y sujeción de piezas.',
    },
    {
        'category': 'herramientas-manuales',
        'name': 'Sierra Manual para Madera',
        'sku': 'HER-SIE-004',
        'description': 'Sierra manual con hoja de acero templado. Mango ergonómico de plástico.',
        'price': Decimal('22.00'),
        'stock': 25,
        'featured': False,
        'material': 'Hoja de acero templado, mango de plástico',
        'dimensiones': '50cm de largo',
        'peso': Decimal('0.5'),
        'color': 'Verde y Negro',
        'voltaje': '',
        'potencia': '',
        'marca': 'Irwin',
        'garantia': '1 año',
        'uso_recomendado': 'Para corte de madera, tableros y materiales de carpintería.',
    },
    
    # Herramientas Eléctricas
    {
        'category': 'herramientas-electricas',
        'name': 'Taladro Eléctrico Profesional 800W',
        'sku': 'HE-TAL-001',
        'description': 'Taladro de impacto profesional con regulador de velocidad y reverse. Ideal para trabajos pesados en concreto, metal y madera.',
        'price': Decimal('89.99'),
        'stock': 15,
        'featured': True,
        'material': 'Carcasa de plástico ABS reforzado',
        'dimensiones': '28cm x 8cm x 22cm',
        'peso': Decimal('2.5'),
        'color': 'Azul y Negro',
        'voltaje': '110V',
        'potencia': '800W',
        'marca': 'DeWalt',
        'garantia': '2 años',
        'uso_recomendado': 'Perforación en concreto, metal, madera y plástico. Ideal para uso profesional en construcción.',
    },
    {
        'category': 'herramientas-electricas',
        'name': 'Sierra Circular 1500W con Láser',
        'sku': 'HE-SIE-001',
        'description': 'Sierra circular de alta potencia con guía láser para cortes precisos. Incluye hoja de 7.25 pulgadas y protector de seguridad.',
        'price': Decimal('125.50'),
        'stock': 8,
        'featured': True,
        'material': 'Aluminio fundido y acero',
        'dimensiones': '35cm x 25cm x 25cm',
        'peso': Decimal('4.2'),
        'color': 'Naranja y Negro',
        'voltaje': '110V',
        'potencia': '1500W',
        'marca': 'Makita',
        'garantia': '3 años',
        'uso_recomendado': 'Corte de madera, plástico y materiales compuestos. Para carpintería profesional.',
    },
    {
        'category': 'herramientas-electricas',
        'name': 'Amoladora Angular 900W 4.5 pulgadas',
        'sku': 'HE-AMO-001',
        'description': 'Amoladora angular profesional con protector ajustable y empuñadura lateral. Perfecta para corte y desbaste de metal.',
        'price': Decimal('67.00'),
        'stock': 12,
        'featured': True,
        'material': 'Carcasa metálica con recubrimiento plástico',
        'dimensiones': '30cm x 10cm x 15cm',
        'peso': Decimal('2.1'),
        'color': 'Verde y Negro',
        'voltaje': '110V',
        'potencia': '900W',
        'marca': 'Bosch',
        'garantia': '1 año',
        'uso_recomendado': 'Corte y desbaste de metal, concreto y piedra. Para uso industrial y profesional.',
    },
    
    # Pinturas
    {
        'category': 'pinturas',
        'name': 'Pintura Látex Blanca 1 Galón',
        'sku': 'PIN-LAT-001',
        'description': 'Pintura látex interior/exterior color blanco. Rendimiento aproximado: 10-12 m² por galón.',
        'price': Decimal('25.99'),
        'stock': 40,
        'featured': True,
        'material': 'Resina acrílica, pigmentos, aditivos',
        'dimensiones': '15cm x 15cm x 25cm (galón)',
        'peso': Decimal('3.8'),
        'color': 'Blanco',
        'voltaje': '',
        'potencia': '',
        'marca': 'Sherwin Williams',
        'garantia': '5 años',
        'uso_recomendado': 'Para paredes interiores y exteriores. Resistente a la intemperie.',
    },
    {
        'category': 'pinturas',
        'name': 'Brocha 3 Pulgadas',
        'sku': 'PIN-BRO-002',
        'description': 'Brocha profesional de 3 pulgadas con cerdas sintéticas. Mango de madera barnizada.',
        'price': Decimal('6.50'),
        'stock': 90,
        'featured': False,
        'material': 'Cerdas sintéticas, mango de madera',
        'dimensiones': '30cm de largo total',
        'peso': Decimal('0.2'),
        'color': 'Café y Negro',
        'voltaje': '',
        'potencia': '',
        'marca': 'Purdy',
        'garantia': 'N/A',
        'uso_recomendado': 'Para aplicación de pinturas, barnices y selladores.',
    },
    {
        'category': 'pinturas',
        'name': 'Rodillo con Extensión',
        'sku': 'PIN-ROD-003',
        'description': 'Rodillo de 9 pulgadas con extensión telescópica. Incluye 2 recambios.',
        'price': Decimal('16.75'),
        'stock': 45,
        'featured': False,
        'material': 'Marco de aluminio, mango de plástico',
        'dimensiones': '50cm - 150cm (extensible)',
        'peso': Decimal('1.2'),
        'color': 'Naranja y Negro',
        'voltaje': '',
        'potencia': '',
        'marca': 'Wooster',
        'garantia': '6 meses',
        'uso_recomendado': 'Para pintado rápido de paredes y techos. Extensión telescópica para mayor alcance.',
    },
    {
        'category': 'pinturas',
        'name': 'Cinta de Pintor 2"',
        'sku': 'PIN-CIN-004',
        'description': 'Cinta adhesiva de baja adherencia para pintar. Rollo de 50 metros.',
        'price': Decimal('4.99'),
        'stock': 120,
        'featured': False,
        'material': 'Papel crepé con adhesivo',
        'dimensiones': '2" de ancho x 50m de largo',
        'peso': Decimal('0.15'),
        'color': 'Blanco crema',
        'voltaje': '',
        'potencia': '',
        'marca': '3M',
        'garantia': 'N/A',
        'uso_recomendado': 'Para protección de bordes y delimitación de áreas al pintar.',
    },
    
    # Electricidad
    {
        'category': 'electricidad',
        'name': 'Cable Eléctrico 2x14 (10m)',
        'sku': 'ELE-CAB-001',
        'description': 'Cable eléctrico calibre 14 AWG, 2 hilos. Rollo de 10 metros. Certificado.',
        'price': Decimal('18.50'),
        'stock': 55,
        'featured': True,
        'material': 'Cobre electrolítico, aislamiento PVC',
        'dimensiones': '10cm de diámetro (rollo)',
        'peso': Decimal('1.8'),
        'color': 'Blanco y Negro',
        'voltaje': '600V',
        'potencia': '15A máximo',
        'marca': 'Southwire',
        'garantia': 'N/A',
        'uso_recomendado': 'Para instalaciones eléctricas residenciales, circuitos de 15 amperios.',
    },
    {
        'category': 'electricidad',
        'name': 'Bombillo LED 9W Luz Blanca',
        'sku': 'ELE-BOM-002',
        'description': 'Bombillo LED de 9W equivalente a 60W incandescente. Luz blanca fría, base E27.',
        'price': Decimal('5.99'),
        'stock': 200,
        'featured': True,
        'material': 'Plástico policarbonato, aluminio',
        'dimensiones': '12cm de alto x 6cm de diámetro',
        'peso': Decimal('0.1'),
        'color': 'Blanco',
        'voltaje': '110V - 240V',
        'potencia': '9W (equivalente a 60W incandescente)',
        'marca': 'Philips',
        'garantia': '3 años',
        'uso_recomendado': 'Iluminación general de interiores, ahorro energético.',
    },
    {
        'category': 'electricidad',
        'name': 'Interruptor Simple',
        'sku': 'ELE-INT-003',
        'description': 'Interruptor simple de pared, color blanco. 15A, 120V.',
        'price': Decimal('3.25'),
        'stock': 150,
        'featured': False,
        'material': 'Termoplástico, contactos de cobre',
        'dimensiones': '8.5cm x 4.5cm',
        'peso': Decimal('0.05'),
        'color': 'Blanco',
        'voltaje': '120V',
        'potencia': '15A',
        'marca': 'Legrand',
        'garantia': '1 año',
        'uso_recomendado': 'Para control de iluminación y dispositivos eléctricos en instalaciones residenciales.',
    },
    {
        'category': 'electricidad',
        'name': 'Tomacorriente Doble',
        'sku': 'ELE-TOM-004',
        'description': 'Tomacorriente doble polarizado, color blanco. 15A, 120V.',
        'price': Decimal('4.50'),
        'stock': 140,
        'featured': False,
        'material': 'Termoplástico, contactos de cobre',
        'dimensiones': '8.5cm x 4.5cm',
        'peso': Decimal('0.08'),
        'color': 'Blanco',
        'voltaje': '120V',
        'potencia': '15A por salida',
        'marca': 'Schneider Electric',
        'garantia': '1 año',
        'uso_recomendado': 'Para conexión de dispositivos eléctricos en instalaciones residenciales y comerciales.',
    },
    
    # Plomería
    {
        'category': 'plomeria',
        'name': 'Codo PVC 1/2" 90°',
        'sku': 'PLO-COD-001',
        'description': 'Codo de PVC de 1/2 pulgada a 90 grados. Material resistente y duradero.',
        'price': Decimal('0.85'),
        'stock': 300,
        'featured': False,
        'material': 'PVC de grado sanitario',
        'dimensiones': '5cm x 5cm x 5cm',
        'peso': Decimal('0.05'),
        'color': 'Blanco',
        'voltaje': '',
        'potencia': '',
        'marca': 'Genérico',
        'garantia': 'N/A',
        'uso_recomendado': 'Para cambio de dirección en tuberías de desagüe y ventilación.',
    },
    {
        'category': 'plomeria',
        'name': 'Tubo PVC 1/2" (3m)',
        'sku': 'PLO-TUB-002',
        'description': 'Tubo de PVC de 1/2 pulgada, longitud 3 metros. Presión 315 PSI.',
        'price': Decimal('6.75'),
        'stock': 75,
        'featured': False,
        'material': 'PVC de grado sanitario',
        'dimensiones': '3m de largo, 2.1cm de diámetro exterior',
        'peso': Decimal('1.2'),
        'color': 'Blanco',
        'voltaje': '',
        'potencia': '',
        'marca': 'Genérico',
        'garantia': 'N/A',
        'uso_recomendado': 'Para sistemas de desagüe, ventilación y conducción de agua.',
    },
    {
        'category': 'plomeria',
        'name': 'Llave de Paso 1/2"',
        'sku': 'PLO-LLA-003',
        'description': 'Llave de paso de bola de 1/2 pulgada. Acabado cromado.',
        'price': Decimal('12.50'),
        'stock': 40,
        'featured': False,
        'material': 'Latón cromado, bola de acero inoxidable',
        'dimensiones': '8cm de largo total',
        'peso': Decimal('0.25'),
        'color': 'Plateado',
        'voltaje': '',
        'potencia': '',
        'marca': 'Genérico',
        'garantia': 'N/A',
        'uso_recomendado': 'Para control de flujo en tuberías de agua. Cierre total de 1/4 de vuelta.',
    },
    
    # Miscelánea
    {
        'category': 'miscelanea',
        'name': 'Escoba de Plástico',
        'sku': 'MIS-ESC-001',
        'description': 'Escoba de cerdas plásticas resistentes. Mango de metal con rosca estándar.',
        'price': Decimal('8.99'),
        'stock': 65,
        'featured': False,
        'material': 'Cerdas de polipropileno, mango de aluminio',
        'dimensiones': '120cm de alto total',
        'peso': Decimal('0.8'),
        'color': 'Azul y Plateado',
        'voltaje': '',
        'potencia': '',
        'marca': 'Libbey',
        'garantia': '6 meses',
        'uso_recomendado': 'Para limpieza de pisos en interiores. Cerdas resistentes al desgaste.',
    },
    {
        'category': 'miscelanea',
        'name': 'Recogedor de Metal',
        'sku': 'MIS-REC-002',
        'description': 'Recogedor de metal galvanizado con mango largo. Durabilidad garantizada.',
        'price': Decimal('5.75'),
        'stock': 70,
        'featured': False,
        'material': 'Metal galvanizado, mango de madera',
        'dimensiones': '40cm de ancho x 30cm de fondo',
        'peso': Decimal('0.6'),
        'color': 'Plateado y café',
        'voltaje': '',
        'potencia': '',
        'marca': 'Libbey',
        'garantia': '6 meses',
        'uso_recomendado': 'Para recoger basura y residuos. Compatible con escobas estándar.',
    },
    {
        'category': 'miscelanea',
        'name': 'Balde Plástico 10L',
        'sku': 'MIS-BAL-003',
        'description': 'Balde de plástico resistente de 10 litros con asa metálica.',
        'price': Decimal('7.50'),
        'stock': 50,
        'featured': False,
        'material': 'Polipropileno, asa de acero',
        'dimensiones': '30cm de alto x 28cm de diámetro',
        'peso': Decimal('0.4'),
        'color': 'Rojo',
        'voltaje': '',
        'potencia': '',
        'marca': 'Rubbermaid',
        'garantia': '1 año',
        'uso_recomendado': 'Para limpieza, mezcla de materiales, almacenamiento de líquidos.',
    },
    {
        'category': 'miscelanea',
        'name': 'Candado de Seguridad 40mm',
        'sku': 'MIS-CAN-004',
        'description': 'Candado de seguridad con arco de 40mm. Incluye 3 llaves.',
        'price': Decimal('11.99'),
        'stock': 45,
        'featured': True,
        'material': 'Cuerpo de acero forjado, arco templado',
        'dimensiones': '8cm x 6cm x 2.5cm',
        'peso': Decimal('0.35'),
        'color': 'Negro',
        'voltaje': '',
        'potencia': '',
        'marca': 'Master Lock',
        'garantia': '1 año',
        'uso_recomendado': 'Para seguridad de puertas, portones, cadenas y herrajes.',
    }
]

products_created = 0
products_updated = 0

for prod_data in products_data:
    category = categories[prod_data['category']]
    prod, created = Product.objects.update_or_create(
        sku=prod_data['sku'],
        defaults={
            'category': category,
            'name': prod_data['name'],
            'description': prod_data['description'],
            'price': prod_data['price'],
            'stock': prod_data['stock'],
            'featured': prod_data['featured'],
            'is_active': True,
            # Campos adicionales de especificaciones
            'material': prod_data.get('material', ''),
            'dimensiones': prod_data.get('dimensiones', ''),
            'peso': prod_data.get('peso', Decimal('0.0')),
            'color': prod_data.get('color', ''),
            'voltaje': prod_data.get('voltaje', ''),
            'potencia': prod_data.get('potencia', ''),
            'marca': prod_data.get('marca', ''),
            'garantia': prod_data.get('garantia', ''),
            'uso_recomendado': prod_data.get('uso_recomendado', ''),
        }
    )
    if created:
        products_created += 1
        status = "✅ Creado"
    else:
        products_updated += 1
        status = "🔄 Actualizado"
    
    featured = "⭐" if prod.featured else ""
    print(f"  {status}: {prod.name} {featured} - ${prod.price} ({prod.stock} unidades)")

print("\n" + "="*60)
print("✅ Base de datos poblada exitosamente!")
print("="*60)
print("\n📊 Resumen:")
print(f"   Categorías: {Category.objects.count()}")
print(f"   Productos totales: {Product.objects.count()}")
print(f"   Productos creados: {products_created}")
print(f"   Productos actualizados: {products_updated}")
print(f"   Productos destacados: {Product.objects.filter(featured=True).count()}")
print("\n🎉 ¡Tu tienda está lista para empezar a vender!")
print("\n💡 Consejos:")
print("   1. Accede al admin en /admin/ para ver todos los productos")
print("   2. Crea un usuario de prueba en /registro/")
print("   3. Agrega imágenes a los productos desde el admin")
print("   4. Prueba el flujo completo de compra")
print("   5. Usa la función de comparación para ver las especificaciones")
print("\n🚀 Inicia el servidor con: python manage.py runserver\n")