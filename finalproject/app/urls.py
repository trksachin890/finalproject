from django.urls import path
from app.views import *
from app import views

urlpatterns = [
    path("firstpage/", views.firstpage,name="firstpage"),
    path("",views.INDEX,name='home'),
    path("home/",views.INDEX,name='home'),
    path('base/',views.BASE,name='base'),
    path('register/',views.HandleRegister,name="register"),
    path('login/',views.HandleLogin,name="login"),
    path('logout/',views.HandleLogout,name="logout"),
    path('contact/',views.CONTACT,name="contact"),

    path('search/',views.SEARCH, name="search"),

    path('home/<str:id>',views.SingleProductImage,name='singleproduct'),
    path("add-review/", views.add_review, name="add_review"),

    
]


