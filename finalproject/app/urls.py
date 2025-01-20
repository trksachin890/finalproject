from django.urls import path
from app.views import *
from app import views

from django.contrib.auth import views as auth_views  # Import Django's built-in views as auth_views

urlpatterns = [
    path("", views.HOME,name="home"),
#     
    path("products/",views.PRODUCT,name='products'),
    # path('products/<str:id>',views.PRODUCT_DETAIL_PAGE,name="product_detail"),
    path('products_details/<str:id>',views.PRODUCT_DETAIL_PAGE,name="product_detail"),

    path('base/',views.BASE,name='base'),
    path('register/',views.HandleRegister,name="register"),
    path('login/',views.HandleLogin,name="login"),
    path('logout/',views.HandleLogout,name="logout"),
    path('contact/',views.Contact_Page,name="contact"),

    path('search/',views.SEARCH, name="search"),

    
    path("add-review/", views.add_review, name="add_review"),


   path("wishlist/<int:id>/", views.add_to_wishlist, name="add_to_wishlist"),

    path("wishlist/",views.wishlist,name="wishlist"),
     
    # yaha wishlist ma problem xa but stll save vairako a
    
    path('place_order/',views.PLACE_ORDER, name='place_order'),





    path("about/",views.about,name="about"),




    path('order_item/',views.ORDER_ITEM,name='order_item'),
    # cart
    path('cart/add/<int:id>/', views.cart_add, name='cart_add'),
    path('cart/item_clear/<int:id>/', views.item_clear, name='item_clear'),
    path('cart/item_increment/<int:id>/',views.item_increment, name='item_increment'),
    path('cart/item_decrement/<int:id>/',views.item_decrement, name='item_decrement'),
    path('cart/cart_clear/', views.cart_clear, name='cart_clear'),
    path('cart/cart-detail/',views.cart_detail,name='cart_detail'),
    


    # resetpassword
   # urls.py



    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),


    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),


    

    
]

