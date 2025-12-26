# shop/views/compare.py
"""
Vistas para el comparador de productos.

Permite comparar hasta 4 productos simultáneamente,
mostrando sus especificaciones técnicas lado a lado.
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from ..models import Product


def compare_products(request):
    """
    Vista principal del comparador.
    
    Recibe IDs de productos via GET y muestra tabla comparativa.
    Ejemplo: /comparar/?ids=1,2,3
    
    ✅ OPTIMIZADO: select_related para category
    """
    # Obtener IDs de productos desde la URL
    product_ids = request.GET.get('ids', '')
    
    if not product_ids:
        # Sin productos seleccionados
        return render(request, 'shop/compare/compare.html', {
            'products': [],
            'error': 'No hay productos seleccionados para comparar.'
        })
    
    # Convertir string "1,2,3" a lista [1, 2, 3]
    try:
        product_ids = [int(id.strip()) for id in product_ids.split(',') if id.strip()]
    except ValueError:
        return render(request, 'shop/compare/compare.html', {
            'products': [],
            'error': 'IDs de productos inválidos.'
        })
    
    # Validar cantidad (máximo 4 productos)
    if len(product_ids) < 2:
        return render(request, 'shop/compare/compare.html', {
            'products': [],
            'error': 'Selecciona al menos 2 productos para comparar.'
        })
    
    if len(product_ids) > 4:
        product_ids = product_ids[:4]  # Limitar a 4
    
    # ✅ OPTIMIZACIÓN: Cargar productos con category
    products = Product.objects.filter(
        id__in=product_ids,
        is_active=True
    ).select_related('category')
    
    if not products.exists():
        return render(request, 'shop/compare/compare.html', {
            'products': [],
            'error': 'No se encontraron productos válidos.'
        })
    
    # Preparar datos para comparación
    comparison_data = prepare_comparison_data(products)
    
    context = {
        'products': products,
        'comparison_data': comparison_data,
        'product_count': len(products),
    }
    
    return render(request, 'shop/compare/compare.html', context)


def prepare_comparison_data(products):
    """
    Prepara los datos para la tabla de comparación.
    
    Agrupa las especificaciones por categorías y detecta diferencias.
    
    Args:
        products: QuerySet de productos
        
    Returns:
        dict: Datos estructurados para el template
    """
    # Definir estructura de comparación
    comparison_structure = {
        'Información Básica': [
            {'key': 'name', 'label': 'Nombre'},
            {'key': 'sku', 'label': 'SKU'},
            {'key': 'category__name', 'label': 'Categoría'},
            {'key': 'marca', 'label': 'Marca'},
        ],
        'Especificaciones Físicas': [
            {'key': 'material', 'label': 'Material'},
            {'key': 'dimensiones', 'label': 'Dimensiones'},
            {'key': 'peso', 'label': 'Peso', 'unit': 'kg'},
            {'key': 'color', 'label': 'Color'},
        ],
        'Especificaciones Técnicas': [
            {'key': 'voltaje', 'label': 'Voltaje'},
            {'key': 'potencia', 'label': 'Potencia'},
        ],
        'Información Comercial': [
            {'key': 'price', 'label': 'Precio', 'format': 'currency'},
            {'key': 'stock', 'label': 'Disponibilidad', 'format': 'stock'},
            {'key': 'garantia', 'label': 'Garantía'},
            {'key': 'uso_recomendado', 'label': 'Uso Recomendado'},
        ],
    }
    
    # Procesar datos
    result = {}
    
    for category_name, fields in comparison_structure.items():
        category_data = []
        
        for field_config in fields:
            field_key = field_config['key']
            field_label = field_config['label']
            
            # Obtener valores de todos los productos
            values = []
            for product in products:
                # Manejar campos anidados (ej: category__name)
                if '__' in field_key:
                    parts = field_key.split('__')
                    value = product
                    for part in parts:
                        value = getattr(value, part, None)
                        if value is None:
                            break
                else:
                    value = getattr(product, field_key, None)
                
                # Formatear valor
                formatted_value = format_field_value(
                    value, 
                    field_config.get('format'),
                    field_config.get('unit')
                )
                
                values.append(formatted_value)
            
            # Detectar si hay diferencias
            has_difference = len(set(values)) > 1
            
            # Solo incluir si al menos un producto tiene valor
            if any(v and v != 'No especificado' for v in values):
                category_data.append({
                    'label': field_label,
                    'values': values,
                    'has_difference': has_difference,
                })
        
        # Solo incluir categoría si tiene datos
        if category_data:
            result[category_name] = category_data
    
    return result


def format_field_value(value, format_type=None, unit=None):
    """
    Formatea un valor de campo para mostrar.
    
    Args:
        value: Valor del campo
        format_type: Tipo de formato (currency, stock, etc)
        unit: Unidad a agregar (kg, cm, etc)
        
    Returns:
        str: Valor formateado
    """
    # Valor vacío
    if value is None or value == '':
        return 'No especificado'
    
    # Formato de moneda
    if format_type == 'currency':
        return f'${value}'
    
    # Formato de stock
    if format_type == 'stock':
        if value == 0:
            return '<span class="text-danger">Agotado</span>'
        elif value < 10:
            return f'<span class="text-warning">{value} unidades</span>'
        else:
            return f'<span class="text-success">{value} unidades</span>'
    
    # Agregar unidad
    if unit and value:
        return f'{value} {unit}'
    
    return str(value)


@require_http_methods(["POST"])
def add_to_compare(request):
    """
    API para agregar producto a la lista de comparación.
    Maneja la selección vía AJAX.
    
    Returns:
        JSON con estado de la comparación
    """
    product_id = request.POST.get('product_id')
    
    if not product_id:
        return JsonResponse({
            'success': False,
            'message': 'ID de producto no proporcionado'
        })
    
    # Obtener lista actual de comparación desde sesión
    compare_list = request.session.get('compare_list', [])
    
    try:
        product_id = int(product_id)
    except ValueError:
        return JsonResponse({
            'success': False,
            'message': 'ID inválido'
        })
    
    # Verificar que el producto existe
    if not Product.objects.filter(id=product_id, is_active=True).exists():
        return JsonResponse({
            'success': False,
            'message': 'Producto no encontrado'
        })
    
    # Validar límite de 4 productos
    if product_id in compare_list:
        return JsonResponse({
            'success': False,
            'message': 'Este producto ya está en la comparación',
            'compare_count': len(compare_list)
        })
    
    if len(compare_list) >= 4:
        return JsonResponse({
            'success': False,
            'message': 'Máximo 4 productos para comparar',
            'compare_count': len(compare_list)
        })
    
    # Agregar a la lista
    compare_list.append(product_id)
    request.session['compare_list'] = compare_list
    request.session.modified = True
    
    return JsonResponse({
        'success': True,
        'message': 'Producto agregado a comparación',
        'compare_count': len(compare_list),
        'compare_list': compare_list
    })


@require_http_methods(["POST"])
def remove_from_compare(request):
    """
    API para remover producto de la lista de comparación.
    """
    product_id = request.POST.get('product_id')
    
    if not product_id:
        return JsonResponse({
            'success': False,
            'message': 'ID no proporcionado'
        })
    
    try:
        product_id = int(product_id)
    except ValueError:
        return JsonResponse({
            'success': False,
            'message': 'ID inválido'
        })
    
    # Obtener y modificar lista
    compare_list = request.session.get('compare_list', [])
    
    if product_id in compare_list:
        compare_list.remove(product_id)
        request.session['compare_list'] = compare_list
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'message': 'Producto removido',
            'compare_count': len(compare_list),
            'compare_list': compare_list
        })
    else:
        return JsonResponse({
            'success': False,
            'message': 'Producto no está en la comparación',
            'compare_count': len(compare_list)
        })


def get_compare_list(request):
    """
    API para obtener la lista actual de comparación desde la sesión.
    Permite sincronizar el estado del cliente con el servidor.
    
    Returns:
        JSON con la lista actual
    """
    compare_list = request.session.get('compare_list', [])
    
    return JsonResponse({
        'success': True,
        'compare_list': compare_list,
        'compare_count': len(compare_list)
    })


@require_http_methods(["POST"])
def clear_compare(request):
    """
    API para limpiar toda la lista de comparación.
    """
    request.session['compare_list'] = []
    request.session.modified = True
    
    return JsonResponse({
        'success': True,
        'message': 'Comparación limpiada',
        'compare_count': 0
    })