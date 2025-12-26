from django.urls import path
from . import views
from . import views_test_errors

app_name = 'shop'

urlpatterns = [

    # ==========================================
    # URLs DE PRUEBA PARA ERRORES (Solo desarrollo)
    # ==========================================
    path('test-errors/404/', views_test_errors.test_404, name='test_404'),
    path('test-errors/500/', views_test_errors.test_500, name='test_500'),
    path('test-errors/429/', views_test_errors.test_429, name='test_429'),

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
    path('cambiar-contrasena/', views.change_password, name='change_password'),

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

    # Reviews
    path('producto/<int:product_id>/agregar-review/', views.add_review, name='add_review'),
    path('review/<int:review_id>/editar/', views.edit_review, name='edit_review'),
    path('review/<int:review_id>/eliminar/', views.delete_review, name='delete_review'),
    path('review/<int:review_id>/util/', views.mark_review_helpful, name='mark_review_helpful'),
    path('producto/<int:product_id>/reviews/', views.product_reviews, name='product_reviews'),
    
    # Wishlist
    path('lista-deseos/', views.wishlist_view, name='wishlist'),
    path('agregar-a-favoritos/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('quitar-de-favoritos/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('toggle-favorito/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('mover-al-carrito/<int:item_id>/', views.move_to_cart, name='move_to_cart'),
    path('vaciar-favoritos/', views.clear_wishlist, name='clear_wishlist'),

    # Páginas estáticas
    path('sobre-nosotros/', views.about_us, name='about_us'),
    path('contacto/', views.contact, name='contact'),
    path('preguntas-frecuentes/', views.faq, name='faq'),

    # Comparador de productos
    path('comparar/', views.compare_products, name='compare_products'),
    path('comparar/agregar/', views.add_to_compare, name='add_to_compare'),
    path('comparar/remover/', views.remove_from_compare, name='remove_from_compare'),
    path('comparar/limpiar/', views.clear_compare, name='clear_compare'),
]
