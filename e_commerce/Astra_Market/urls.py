from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('products/', views.products, name='products'),
    path('category/', views.category, name='category'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('cart/', views.cart, name='cart'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('orders/', views.orders, name='orders'),
    path('orders/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('orders/<int:order_id>/confirm-cancel/', views.confirm_cancel_order, name='confirm_cancel_order'),
    path('checkout/', views.checkout, name='checkout'),
    path('confirm-checkout/', views.confirm_checkout, name='confirm_checkout'),
    path('support/', views.support, name='support'),
    path('products/<slug:slug>/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('products/<slug:slug>/remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
    path('products/<slug:slug>/update-cart-quantity/', views.update_cart_quantity, name='update_cart_quantity'),
    path('products/<slug:slug>/add-to-wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('products/<slug:slug>/remove-from-wishlist/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),
]
