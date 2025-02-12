"""
URL configuration for finalproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from app.views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.models import *
from app.admin import *

from django_otp.admin import OTPAdminSite
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_totp.admin import TOTPDeviceAdmin



class OTPAdmin(OTPAdminSite):
   pass

admin_site = OTPAdmin(name='OTPAdmin')
admin_site.register(User)

# Registering Models
admin_site.register(VehicleType, VehicletypeAdmin)
admin_site.register(Product, ProductAdmin)
admin_site.register(Category, CategoryAdmin)
admin_site.register(Brand, BrandAdmin)
admin_site.register(FilterPrice)
# admin.site.register(CartOrder, CartOrderAdmin)
admin_site.register(Images)
admin_site.register(ProductReview, ProductReviewAdmin)
admin_site.register(Wishlist, WishlistAdmin)
admin_site.register(Order, OrderAdmin)

admin_site.register(OrderItem, OrderItemAdmin)

admin_site.register(Tag, TagAdmin)
admin_site.register(Contact_us)
admin_site.register(ABOUT)
admin_site.register(TOTPDevice, TOTPDeviceAdmin)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('adminotp/', admin_site.urls),
    path("",include("app.urls")),
    path('ratings/', include('star_ratings.urls', namespace='ratings')),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL , document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL , document_root=settings.MEDIA_ROOT)
