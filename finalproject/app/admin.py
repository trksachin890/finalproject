from django.contrib import admin
from django.utils.html import mark_safe
from app.models import *

# Inline for Product Images
class ImagesTublerinline(admin.TabularInline):
    model=Images
    

# Admin for Product
class ProductAdmin(admin.ModelAdmin):
    inlines = [ImagesTublerinline]
    list_display = ['name', 'product_image', 'category', 'price', 'stock', 'condition', 'vehicletype']
    

# Admin for Category
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_image']

# Admin for Brand
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name']

# Admin for Vehicletype
class VehicletypeAdmin(admin.ModelAdmin):
    list_display = ['name']

# Admin for Cart Order
class CartOrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'price', 'order_date', 'product_status']

# Admin for Cart Order Items

# Admin for Product Review
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'date']

# Admin for Wishlist
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'date']

# Admin for Address
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'address', 'firstname','lastname']

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity','price','total']
# Admin for Tags
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']

# Registering Models
admin.site.register(VehicleType, VehicletypeAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(FilterPrice)
# admin.site.register(CartOrder, CartOrderAdmin)
admin.site.register(Images)
admin.site.register(ProductReview, ProductReviewAdmin)
admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(Order, OrderAdmin)

admin.site.register(OrderItem, OrderItemAdmin)

admin.site.register(Tag, TagAdmin)
admin.site.register(Contact_us)
admin.site.register(ABOUT)