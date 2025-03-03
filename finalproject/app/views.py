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
from django.http import JsonResponse
from finalproject import settings


from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Wishlist

from .recommendation import recommend_products








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




@login_required(login_url="/login/")
def add_to_wishlist(request, id):
    product = get_object_or_404(Product, id=id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    
    if created:
        message = "Added to Wishlist successfully!"
    else:
        message = "Product is already in your Wishlist."

    # Handle AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({"success": True, "message": message})

    # Redirect back to the same page where the request came from
    referer_url = request.META.get('HTTP_REFERER', 'wishlist')  # Defaults to wishlist page if no referer
    return redirect(referer_url)



@login_required(login_url="/login/")
def wishlist(request):
    if request.user.is_authenticated:
        wishlists = Wishlist.objects.filter(user=request.user)
         # Count the number of wishlist items

    else:
        wishlists = None  # No wishlist for unauthenticated users
    context = {'wishlists': wishlists,
}
    return render(request, 'wishlist/wishlist.html', context)


@login_required(login_url="/login/")
def remove_from_wishlist(request, id):
    wishlist_item = get_object_or_404(Wishlist, user=request.user, product_id=id)
    wishlist_item.delete()
    
    # Redirect back to the same page where the request came from
    referer_url = request.META.get("HTTP_REFERER", "wishlist")  # Defaults to 'wishlist' if no referrer is found
    return redirect(referer_url)



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
        return redirect('products')
        
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
    cart = request.session.get('cart', {})
    cart_total_amount = sum(float(item['price']) * int(item['quantity']) for item in cart.values())

    

    if request.method == "POST":
        

        for key, value in cart.items():
            print(f"\U0001F50D Processing Cart Item: {value}")  # Debugging

            product_id = value.get('product_id')  # FIXED: Correct key
            if not product_id:
                print(f"⚠️ Skipping item {key} due to missing product_id")
                continue  # Skip invalid entries

            try:
                product_instance = Product.objects.get(id=int(product_id))  # Convert to int
                print(f"✅ Product {product_instance.name} found!")

                order_item = OrderItem.objects.create(
                    user=request.user,
                    product=product_instance,
                    price=float(value['price']),
                    quantity=int(value['quantity']),
                    image=value['image'],
                    total=float(value['price']) * int(value['quantity'])
                )

                print("✅ OrderItem successfully created:", order_item)

            except (ValueError, Product.DoesNotExist):
                print(f"❌ Invalid or missing product ID: {product_id}")
                continue  # Prevent crashes

        request.session['cart'] = {}  # Clear the cart after saving
        print()
        return redirect('place_order')

    return render(request, 'core/place/order_item.html', {
        'cart': cart,
        'cart_total_amount': cart_total_amount
    })



@login_required(login_url="/login/")
def PLACE_ORDER(request):
    user = request.user
    cart_items = request.session.get('cart', {})
    total_amount = sum(float(item['price']) * int(item['quantity']) for item in cart_items.values())

    

    if request.method == 'POST':
        firstname = request.POST.get('firstname', user.first_name)
        lastname = request.POST.get('lastname', user.last_name)
        address = request.POST.get('address')
        city = request.POST.get('city')
        phone = request.POST.get('phone')
        email = request.POST.get('email', user.email)

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

        for item in cart_items.values():
            product_id = item.get('id')  # Get product ID from session
            try:
                product_instance = Product.objects.get(id=product_id)  # Fetch product
               
                OrderItem.objects.create(
                    user=user,
                    order=order,
                    product=product_instance,  # Store Product instance
                    image=item['image'],
                    quantity=int(item['quantity']),
                    price=float(item['price']),
                    total=float(item['price']) * int(item['quantity']),
                )
            except Product.DoesNotExist:
                print(f"Product with ID {product_id} does not exist.")  # Debugging

        request.session['cart'] = {}  
        return render(request, 'core/thanks/thanks.html')

    context = {
        'user': user,
        'cart_items': cart_items,
        'total_amount': total_amount,
        
    }
    print(context)
    return render(request, 'core/place/placeorder.html', context)



@login_required(login_url="/login/")
def Check_out(request):
    user = request.user
    cart_items = request.session.get('cart', {})
    total_amount = sum(float(item['price']) * int(item['quantity']) for item in cart_items.values())

    context = {
        'user': user,
        'cart_items': cart_items,
        'total_amount': total_amount
    }

    return render(request, 'core/placeorder.html', context)



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



@login_required(login_url="/login/")
def dashbord(request):
    orders = Order.objects.filter(user=request.user).order_by("-date")  # Get user orders
    total_spent = 0  # Initialize total amount spent

    order_details = []
    for order in orders:
        items = OrderItem.objects.filter(user=request.user)  # ✅ Filter OrderItem by user
        order_total = sum(item.total for item in items)  # Calculate total for this order
        total_spent += order_total  # Add to the user's total spending

        order_details.append({
            "order": order,
            "items": items,
            "order_total": order_total,  # Include order total for display
        })

    context = {
        "order_details": order_details,
        "total_spent": total_spent,  # Pass total amount spent
    }

    return render(request, "dashbord/dashbord.html", context)


from django.shortcuts import render
from django.db.models import Q
from .recommendation import recommend_products
from .models import Product, Category, Brand, VehicleType

def recommended_products_view(request):
    category_filter = request.GET.get('category', '')
    brand_filter = request.GET.get('brand', '')
    vehicletype_filter = request.GET.get('vehicletype', '')

    related_products, best_products = recommend_products(user=request.user, top_n=10)

    # Apply filters to related products
    if category_filter:
        related_products = [product for product in related_products if product.category.id == int(category_filter)]
    if brand_filter:
        related_products = [product for product in related_products if product.brand.id == int(brand_filter)]
    if vehicletype_filter:
        related_products = [product for product in related_products if product.vehicletype.id == int(vehicletype_filter)]

    # Apply filters to best products
    if category_filter:
        best_products = [product for product in best_products if product.category.id == int(category_filter)]
    if brand_filter:
        best_products = [product for product in best_products if product.brand.id == int(brand_filter)]
    if vehicletype_filter:
        best_products = [product for product in best_products if product.vehicletype.id == int(vehicletype_filter)]

    # Get all categories, brands, and vehicle types for filters
    categories = Category.objects.all()
    brands = Brand.objects.all()
    vehicletypes = VehicleType.objects.all()

    return render(request, 'recommendation/recommendation.html', {
        'related_products': related_products,
        'best_products': best_products,
        'categories': categories,
        'brands': brands,
        'vehicletypes': vehicletypes,
    })   





def search_suggestions(request):
    query = request.GET.get('query', '')
    suggestions = []
    recommendations = []
    
    if query:
        # Fetch product names that match the query
        suggestions = Product.objects.filter(status='PUBLIC', name__icontains=query).values_list('name', flat=True)[:10]
        
        # Fetch recommended product names based on the query
        recommendations = Product.objects.filter(status='PUBLIC', name__icontains=query).exclude(name__in=suggestions).values_list('name', flat=True)[:10]
    
    return JsonResponse({'suggestions': list(suggestions), 'recommendations': list(recommendations)}, safe=False)

# --------------------------------edit rating------------------------------
@login_required
def edit_review(request, review_id):
    review = get_object_or_404(ProductReview, id=review_id, user=request.user)

    if request.method == "POST":
        new_review_text = request.POST.get("review")
        new_rating = request.POST.get("rating")

        if new_review_text and new_rating:
            review.review = new_review_text
            review.rating = new_rating
            review.save()
            messages.success(request, "Review updated successfully.")
        else:
            messages.error(request, "All fields are required.")

        return redirect("product_detail", id=review.product.id)

    return redirect("home")



# ------------------------------------change password----------------------------------
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

def change_pass(request):
    if request.method == 'POST':
        fm = PasswordChangeForm(request.user, request.POST)
        if fm.is_valid():
            user = fm.save()
            update_session_auth_hash(request, user)  # Prevent logout after password change
            messages.success(request, 'Your password was successfully updated!')
            return redirect('dashbord')  
        else:
            for error in fm.errors.get('__all__', []):  # Show general form errors
                messages.error(request, error)
    else:
        fm = PasswordChangeForm(request.user)

    return render(request, 'changepassword/changepassword.html', {'form': fm})


