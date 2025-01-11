from django.db import models
from django.contrib.auth.models import User
from django.utils.html import mark_safe
from ckeditor.fields import RichTextField
from django.utils import timezone
from shortuuid.django_fields import ShortUUIDField

# Constants
STATUS = (("PUBLIC", "PUBLIC"), ("DRAFT", "DRAFT"))
RATING = (
    (1, "★☆☆☆☆"),
    (2, "★★☆☆☆"),
    (3, "★★★☆☆"),
    (4, "★★★★☆"),
    (5, "★★★★★"),
)
CONDITIONS = (("NEW", "NEW"), ("OLD", "OLD"))
STOCK = (("IN STOCK", "IN STOCK"), ("OUT OF STOCK", "OUT OF STOCK"))

# Helper function
def user_directory_path(instance, filename):
    if hasattr(instance, 'user') and instance.user:
        return f'user_{instance.user.id}/{filename}'
    return f'default/{filename}'

# Models
class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="category")

    class Meta:
        verbose_name_plural = "Categories"

    def category_image(self):
        return mark_safe(f'<img src="{self.image.url}" width="50" height="50" />')

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Brands"

    def __str__(self):
        return self.name

class FilterPrice(models.Model):
    FILTER_PRICE = (
        ("100 TO 1000", "100 TO 1000"),
        ("1000 TO 2000", "1000 TO 2000"),
        ("2000 TO 3000", "2000 TO 3000"),
        ("3000 TO 4000", "3000 TO 4000"),
        ("4000 TO 5000", "4000 TO 5000"),
        ("5000 TO 6000", "5000 TO 6000"),
        ("6000 TO 7000", "6000 TO 7000"),
    )
    price = models.CharField(choices=FILTER_PRICE, max_length=60)

    class Meta:
        verbose_name_plural = "Filter Prices"

    def __str__(self):
        return self.price

class VehicleType(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Vehicle Types"

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.name

class Product(models.Model):
    unique_id = ShortUUIDField(unique=True, max_length=50)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=1.99)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, default=2.99)
    image = models.ImageField(upload_to=user_directory_path)
    information = RichTextField(null=True, blank=True)
    description = RichTextField(null=True, blank=True)
    status = models.CharField(choices=STATUS, max_length=100, default="PUBLIC")
    stock = models.CharField(choices=STOCK, max_length=200, default="IN STOCK")
    condition = models.CharField(choices=CONDITIONS, max_length=100)
    created_date = models.DateTimeField(default=timezone.now)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    vehicletype = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
    filter_price = models.ForeignKey(FilterPrice, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)

    class Meta:
        verbose_name_plural = "Products"

    def product_image(self):
        return mark_safe(f'<img src="{self.image.url}" width="50" height="50" />')

    def __str__(self):
        return self.name

    def get_percentage(self):
        if self.old_price > 0:
            discount = ((self.old_price - self.price) / self.old_price) * 100
            return round(discount, 2)
        return 0

class Images(models.Model):
    image = models.ImageField(upload_to="product-images")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Product Images"

class CartOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    paid_status = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now_add=True)
    product_status = models.CharField(choices=STATUS, max_length=100)

    class Meta:
        verbose_name_plural = "Cart Orders"

class CartOrderItems(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
    product_status = models.CharField(max_length=200)
    invoice_no = models.CharField(max_length=200)
    image = models.ImageField(upload_to="cart-order-items")
    qty = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        verbose_name_plural = "Cart Order Items"

    def cart_order_image(self):
        return mark_safe(f'<img src="{self.image.url}" width="50" height="50" />')

class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    review = models.TextField()
    rating = models.IntegerField(choices=RATING)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Reviews"

    def __str__(self):
        return self.product.name

    def get_rating(self):
        return self.rating




class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    product = models.CharField( max_length=200)
    image = models.ImageField( upload_to='products/Order_Img')
    quantity = models.IntegerField()
    price = models.IntegerField()
    total = models.IntegerField()

    
    class Meta:
        verbose_name_plural = "OrderItem"

    def __str__(self):
        return f"{self.product} (X{self.quantity}) by {self.user.username}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    address = models.TextField(max_length=100)
    city = models.CharField(max_length=100)
    phone = models.IntegerField()
    email = models.EmailField( max_length=100)
   
    amount = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)

    # payment_id = models.CharField(max_length=300,null=True,blank=True)
    # paid = models.BooleanField(default=False,null=True)


    class Meta:
        verbose_name_plural = "Order"

    def __str__(self):
        return self.user.username


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Wishlist"

    def __str__(self):
        return self.product.name



class Contact_us(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    subject = models.CharField(max_length=300)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email



# about
class ABOUT(models.Model):
    title = models.CharField(max_length=200, help_text="Title of the About Page")
    content = models.TextField(help_text="Content of the About Page")
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
