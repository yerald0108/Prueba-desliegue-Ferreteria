from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # Home y productos
    path('', views.home, name='home'),
    path('productos/', views.product_list, name='product_list'),
    path('producto/<int:pk>/', views.product_detail, name='product_detail'),
    
    # Autenticación
    path('registro/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('verificar-email/<str:token>/', views.verify_email, name='verify_email'),
    path('reenviar-verificacion/', views.resend_verification, name='resend_verification'),
    
    # Carrito
    path('carrito/', views.cart_view, name='cart'),
    path('agregar-al-carrito/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('actualizar-carrito/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('eliminar-del-carrito/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('vaciar-carrito/', views.clear_cart, name='clear_cart'),
    
    # Checkout y órdenes
    path('checkout/', views.checkout, name='checkout'),
    path('orden/<int:order_id>/', views.order_detail, name='order_detail'),
    path('mis-ordenes/', views.order_history, name='order_history'),
    
    # Perfil
    path('perfil/', views.profile, name='profile'),

    # Panel de administración
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/ordenes/', views.admin_orders, name='admin_orders'),
    path('admin-panel/orden/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('admin-panel/productos/', views.admin_products, name='admin_products'),
    path('admin-panel/usuarios/', views.admin_users, name='admin_users'),
    path('admin-panel/usuario/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    # path('admin-panel/usuario/<int:user_id>/toggle-active/', views.admin_user_toggle_active, name='admin_user_toggle_active'),
    path('admin-panel/usuario/<int:user_id>/online-status/', views.admin_user_online_status, name='admin_user_online_status'),
    path('admin-panel/producto/<int:product_id>/toggle/', views.admin_toggle_product_status, name='admin_toggle_product_status'),
    path('admin-panel/producto/<int:product_id>/stock/', views.admin_update_stock, name='admin_update_stock'),

    # Gestión de productos en admin
    path('admin-panel/producto/crear/', views.admin_product_create, name='admin_product_create'),
    path('admin-panel/producto/<int:product_id>/editar/', views.admin_product_edit, name='admin_product_edit'),
    path('admin-panel/producto/<int:product_id>/detalle/', views.admin_product_detail, name='admin_product_detail'),
    path('admin-panel/producto/<int:product_id>/eliminar/', views.admin_product_delete, name='admin_product_delete'),
]
