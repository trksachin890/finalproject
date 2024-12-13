from django.urls import path
from app.views import *
from app import views

urlpatterns = [
    path("",views.INDEX,name='home'),
    path('base/',views.BASE,name='base'),
    path('register/',views.HandleRegister,name="register"),
    path('login/',views.HandleLogin,name="login"),
    path('logout/',views.HandleLogout,name="logout")

    
]


