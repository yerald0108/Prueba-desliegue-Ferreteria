"""
Módulo de vistas de administración.

Organiza las vistas del panel de administración en submódulos:
- dashboard: Estadísticas y vista principal
- orders: Gestión de órdenes
- products: Gestión de productos
- users: Gestión de usuarios
"""

from .dashboard import admin_dashboard
from .orders import admin_orders, admin_order_detail
from .products import (
    admin_products,
    admin_product_detail,
    admin_product_create,
    admin_product_edit,
    admin_product_delete,
    admin_toggle_product_status,
    admin_update_stock,
)
from .users import (
    admin_users,
    admin_user_detail,
    admin_user_online_status,
)

__all__ = [
    'admin_dashboard',
    'admin_orders',
    'admin_order_detail',
    'admin_products',
    'admin_product_detail',
    'admin_product_create',
    'admin_product_edit',
    'admin_product_delete',
    'admin_toggle_product_status',
    'admin_update_stock',
    'admin_users',
    'admin_user_detail',
    'admin_user_online_status',
]