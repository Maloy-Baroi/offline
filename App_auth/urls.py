from django.urls import path
from App_auth import views



app_name = 'App_auth'

urlpatterns = [
    path('add-to-cart/', views.add_to_cart, name='add-to-cart'),
    path('cart-view/', views.cart_showcase, name='cart-view'),
    path('update-cart/', views.cart_update, name='update-cart'),
    path('remove-item-from-cart/<int:itemID>/', views.remove_item_from_cart, name='remove-item-from-cart'),
    path('checkout/', views.checkout, name='checkout-page'),
    path('purchase/', views.purchase_action, name='purchase'),
    path('profile-view/', views.profile_view, name='profile-view'),
    path('previous-order/', views.previous_orders, name='previous-order'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registration/', views.register_view, name='registration'),
]

