"""
Refactorización de views.py en módulos organizados.

Esta estructura facilita el mantenimiento y escalabilidad del proyecto.
"""

# ==========================================
# VISTAS PÚBLICAS
# ==========================================
from .products import (
    home,
    product_list,
    product_detail,
)

from .cart import (
    cart_view,
    add_to_cart,
    update_cart_item,
    remove_from_cart,
    clear_cart,
)

from .orders import (
    checkout,
    order_detail,
    order_history,
)

from .auth import (
    register,
    user_login,
    user_logout,
    verify_email,
    resend_verification,
)

from .profile import (
    profile,
    change_password,
)

# ==========================================
# VISTAS DE ADMINISTRACIÓN
# ==========================================
from .admin.dashboard import admin_dashboard
from .admin.orders import admin_orders, admin_order_detail
from .admin.products import (
    admin_products,
    admin_product_detail,
    admin_product_create,
    admin_product_edit,
    admin_product_delete,
    admin_toggle_product_status,
    admin_update_stock,
)
from .admin.users import (
    admin_users,
    admin_user_detail,
    admin_user_online_status,
)

# ==========================================
# VISTAS DE REVIEWS Y WISHLIST
# ==========================================
from .reviews import (
    add_review,
    edit_review,
    delete_review,
    mark_review_helpful,
    product_reviews,
)

from .wishlist import (
    wishlist_view,
    add_to_wishlist,
    remove_from_wishlist,
    toggle_wishlist,
    move_to_cart,
    clear_wishlist,
)

# ==========================================
# PÁGINAS ESTÁTICAS
# ==========================================
from ..pages import (
    about_us,
    contact,
    faq,
)

# ==========================================
# ALL exports (para facilitar imports)
# ==========================================
__all__ = [
    # Public views
    'home',
    'product_list',
    'product_detail',
    'cart_view',
    'add_to_cart',
    'update_cart_item',
    'remove_from_cart',
    'clear_cart',
    'checkout',
    'order_detail',
    'order_history',
    'register',
    'user_login',
    'user_logout',
    'verify_email',
    'resend_verification',
    'profile',
    'change_password',
    # Admin views
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
    # Reviews
    'add_review',
    'edit_review',
    'delete_review',
    'mark_review_helpful',
    'product_reviews',
    # Wishlist
    'wishlist_view',
    'add_to_wishlist',
    'remove_from_wishlist',
    'toggle_wishlist',
    'move_to_cart',
    'clear_wishlist',
    # Páginas estáticas
    'about_us',
    'contact',
    'faq',
]
