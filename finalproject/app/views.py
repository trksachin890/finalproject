from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate,logout
from django.contrib import messages
from django.db.models import Avg
from app.models import *
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.decorators import login_required
from cart.cart import Cart
from django.contrib.auth.views import PasswordResetView

from finalproject import settings
import razorpay

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRECT))









# Create your views here.
def BASE(request):
   
    return render(request,'core/base.html')

def HOME(request):
    product = Product.objects.filter(status="PUBLIC")

    context = {
        "product":product
    }
    return render(request,'core/index.html',context)


# @login_required(login_url="/login/")
def PRODUCT(request):
    product = Product.objects.filter(status='PUBLIC')
    categories = Category.objects.all()
    vehicletype = VehicleType.objects.all()
    brand = Brand.objects.all()
    filter_price = FilterPrice.objects.all()

    tag = Tag.objects.all()
    

    # Get query parameters
    CATID = request.GET.get('category')
    VEHID = request.GET.get('vehicletype')
    BRANDID = request.GET.get('brand')
    PRICE_FILTER_ID = request.GET.get('filter_price')
    ATOZID = request.GET.get('ATOZ')
    ZTOAID = request.GET.get('ZTOA')
    PRICE_LOWTOHIGHID = request.GET.get('PRICE_LOWTOHIGH')
    PRICE_HIGHTOLOWID = request.GET.get('PRICE_HIGHTOLOW')
    NEWTOOLDID = request.GET.get("NEWTOOLD")
    OLDTONEWID = request.GET.get("OLDTONEW")

    TAGID = request.GET.get('tag')
    

    # Apply category, vehicle type, and brand filters
    if CATID:
        product = product.filter(category=CATID)
    if VEHID:
        product = product.filter(vehicletype=VEHID)
    if BRANDID:
        product = product.filter(brand=BRANDID)
    if TAGID:
        product = product.filter(tags=TAGID)

    # Apply price filter
    if PRICE_FILTER_ID:
        product = product.filter(filter_price=PRICE_FILTER_ID)

    # Apply sorting
    if ATOZID:
        product = product.order_by('name')
    elif ZTOAID:
        product = product.order_by('-name')
    elif PRICE_LOWTOHIGHID:
        product = product.order_by('price')
    elif PRICE_HIGHTOLOWID:
        product = product.order_by('-price')
    elif NEWTOOLDID:
        product = product.filter(condition='NEW').order_by('-id')
    elif OLDTONEWID:
        product = product.filter(condition='OLD').order_by('id')

    context = {
        "product": product,
        "category": categories,
        "brand": brand,
        "vehicletype": vehicletype,
        "filter_price": filter_price,
        "tag": tag,
        
    }

    return render(request, 'core/product.html', context)



def HandleRegister(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

        # Check if passwords match
        if pass1 != pass2:
            messages.error(request, "Passwords do not match!")
            return redirect('register')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "This username is already used!")
            return redirect('register')

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "This email is already used!")
            return redirect('register')

        # Create user
        customer = User.objects.create_user(username, email, pass1)
        customer.first_name = first_name
        customer.last_name = last_name
        customer.save()
        messages.success(request, "Registration successful!")
        return redirect('register')

    return render(request, 'auth/auth.html')





def HandleLogin(request):
    # Redirect authenticated users to the home page
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user =  authenticate(username=username,password=password )
        if user is not None:
            login(request,user)
            return redirect('products')
        else:
            messages.error(request, "Incorrect username or password. Please try again.")
            return redirect('login')

    return render(request, 'auth/auth.html')

def HandleLogout(request):
    logout(request)
    
    return  redirect('home')



@login_required(login_url="/login/")

def PRODUCT_DETAIL_PAGE(request, id):
    # Get the product by ID
    prod = Product.objects.filter(id=id).first()

    # Get all reviews for the product, ordered by the most recent
    reviews = ProductReview.objects.filter(product=prod).order_by("-date")
    
    # Calculate the average rating
    avarage_rating = ProductReview.objects.filter(product=prod).aggregate(rating=Avg("rating"))["rating"]
    reviews_with_range = [
        {'review': review, 'rating': list(range(review.rating))}  # Creates a range based on rating
        for review in reviews
    ]
    
    # Pass the product, reviews, and average rating to the template
    context = {
        "prod": prod,
        "review": reviews_with_range ,
        "avarage_rating": round(avarage_rating, 2) if avarage_rating else 0,  # Handle no reviews
    }
    return render(request, 'core/single-product.html', context)




def add_review(request):
    if request.method == "POST":
        # Ensure user is authenticated
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to submit a review.")
            return redirect("login")  # Redirect to login page if not logged in

        product_id = request.POST.get("product_id")
        review_text = request.POST.get("review")
        rating = request.POST.get("rating")
        product = Product.objects.get(id=product_id)
        
        # Create the review
        ProductReview.objects.create(
            user=request.user,
            product=product,
            review=review_text,
            rating=rating,
        )

        # Success message
        messages.success(request, "Your review has been submitted successfully.")

        return redirect("product_detail", id=product_id)  # Redirect back to the product page

    return redirect("home")  # Redirect to home if the request is not POST




def add_to_wishlist(request, id):  # Include the 'id' parameter
    if request.method == "POST" and request.user.is_authenticated:
        product = get_object_or_404(Product, id=id)

        # Check if the product is already in the wishlist
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

        if created:
            messages.success(request, "Added to Wishlist successfully!")
        else:
            messages.info(request, "Product is already in your Wishlist.")

        return redirect("wishlist")  # Redirect to the wishlist page
    else:
        messages.error(request, "You must be logged in to add to Wishlist.")
        return redirect("login")  # Redirect to login if the user is not authenticated


def wishlist(request):
    wishlists = Wishlist.objects.filter(user=request.user)
    context = {'wishlists':wishlists}
    return render(request,'wishlist/wishlist.html',context)





def SEARCH(request):
    query = request.GET.get("query", "")
    
    # Filter products by 'PUBLIC' status and the search query
    if query:
        product = Product.objects.filter(status='PUBLIC', name__icontains=query)
    else:
        product = Product.objects.filter(status='PUBLIC')  # If no query, just return all 'PUBLIC' products
    
    context = {
        "product": product,
    }
    return render(request, 'core/search.html', context)


def Contact_Page(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        contact = Contact_us(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        
        # subject = subject
        # message = message
        # email_from = settings.EMAIL_HOST_USER
        # try:
        #     send_mail(subject,message,email_from,['mrsachin2060@gmail.com'])
        #     contact.save()
        #     return redirect('home')
        # except:
        #     return redirect('contact')

        contact.save()
        return redirect('product')
        
    return render(request,'core/contact.html')




@login_required(login_url="/login/")
def cart_add(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.add(product=product)
    return redirect("products")


@login_required(login_url="/login/")
def item_clear(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.remove(product)
    return redirect("cart_detail")


@login_required(login_url="/login/")
def item_increment(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.add(product=product)
    return redirect("cart_detail")


@login_required(login_url="/login/")
def item_decrement(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.decrement(product=product)
    return redirect("cart_detail")


@login_required(login_url="/login/")
def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect("cart_detail")


@login_required(login_url="/login/")
def cart_detail(request):
    return render(request, 'core/cart_details.html')




@login_required
def ORDER_ITEM(request):
    # Get the cart from the session
    cart = request.session.get('cart', {})
    cart_total_amount = 0  # Initialize the total amount

# Loop through each item in the cart
    for item in cart.values():
        price = float(item['price'])  # Convert price to float
        quantity = int(item['quantity'])  # Convert quantity to integer
        print(type(price))
        print(type(quantity))
        cart_total_amount += price * quantity  # Add the product of price and quantity to the total amount

        

    if request.method == "POST":
        
        for  key,value in cart.items():
            product_name = value['name']
            product_price = float(value['price'])  # Convert price to float
            product_quantity = int(value['quantity'])  # Convert quantity to integer
            product_image = value['image']
            
            # Create an OrderItem instance
            order_item = OrderItem(
                user=request.user,
                # order=order,
                product=product_name,
                price=product_price,
                quantity=product_quantity,
                image=product_image,
                total=cart_total_amount
            )
            order_item.save()

        # Clear the cart after the order is placed
        request.session['cart'] = {}

        # Redirect to a success page or order summary
        return redirect('home')  # Update with your order summary URL name

    return render(request, 'core/place/order_item.html', {
        'cart': cart,
        'cart_total_amount': cart_total_amount
    })



@login_required
def PLACE_ORDER(request):
    if request.method == 'POST':
        # Get user information
        user = request.user
        firstname = request.POST.get('firstname', user.first_name)
        lastname = request.POST.get('lastname', user.last_name)
        address = request.POST.get('address')
        city = request.POST.get('city')
        phone = request.POST.get('phone')
        email = request.POST.get('email')

        # Calculate total amount
        cart_items = request.session.get('cart', [])  # Example: Fetch cart items from session
        total_amount = 0
        for item in cart_items:
            product = Product.objects.get(id=item['product_id'])
            total_amount += product.price * item['quantity']

        # Save the order
        order = Order.objects.create(
            user=user,
            firstname=firstname,
            lastname=lastname,
            address=address,
            city=city,
            phone=phone,
            email=email,
            amount=total_amount,
        )
        print(order)
        # Save order items
        for item in cart_items:
            product = Product.objects.get(id=item['product_id'])
            OrderItem.objects.create(
                user=user,
                product=product.name,
                image=product.image,
                quantity=item['quantity'],
                price=product.price,
                total=product.price * item['quantity'],
            )

        # Clear the cart (optional)
        request.session['cart'] = []

        return redirect('home')

    return render(request, 'core/placeorder.html')



@login_required
def Check_out(request):

    # Set amount (in paise) and other Razorpay parameters


# Get the order ID

# Pass payment details to the template
    
    return render(request, 'core/checkout.html')




def about(request):
    about_content = ABOUT.objects.first()  # Fetch the first About entry
    return render(request, 'about/about.html', {'about': about_content})




# reset

# views.py

class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'registration/password_reset_email.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['protocol'] = self.request.scheme  # 'http' or 'https'
        context['domain'] = self.request.get_host()  # Domain name (e.g., example.com)
        # Ensure uidb64 and token are passed to the context
        context['uidb64'] = kwargs.get('uidb64', '')
        context['token'] = kwargs.get('token', '')
        return context