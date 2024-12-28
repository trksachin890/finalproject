from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate,logout
from django.contrib import messages
from django.db.models import Avg
from app.models import *
from django.contrib.auth.decorators import login_required

from finalproject import settings

# Create your views here.
def BASE(request):
   
    return render(request,'core/base.html')

def firstpage(request):
    product = Product.objects.filter(status="PUBLIC")

    context = {
        "product":product
    }
    return render(request,'core/firstpage.html',context)


# @login_required(login_url="/login/")
def INDEX(request):
    product = Product.objects.filter(status='PUBLIC')
    category = Categories.objects.all()
    vehicletype = VehicleType.objects.all()
    brand = Brand.objects.all()
    filter_price = FilterPrice.objects.all()

    tag = Tags.objects.all()
    

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
        "category": category,
        "brand": brand,
        "vehicletype": vehicletype,
        "filter_price": filter_price,
        "tag": tag,
        
    }

    return render(request, 'core/index.html', context)



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
            return redirect('home')
        else:
            messages.error(request, "Incorrect username or password. Please try again.")
            return redirect('login')

    return render(request, 'auth/auth.html')

def HandleLogout(request):
    logout(request)
    
    return  redirect('home')



@login_required(login_url="/login/")

def SingleProductImage(request, id):
    # Get the product by ID
    prod = Product.objects.filter(id=id).first()

    # Get all reviews for the product, ordered by the most recent
    review = ProductReview.objects.filter(product=prod).order_by("-date")

    # Calculate the average rating
    avarage_rating = ProductReview.objects.filter(product=prod).aggregate(rating=Avg("rating"))["rating"]

    # Pass the product, reviews, and average rating to the template
    context = {
        "prod": prod,
        "review": review,
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

        return redirect("singleproduct", id=product_id)  # Redirect back to the product page

    return redirect("home")  # Redirect to home if the request is not POST



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


def CONTACT(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        contact = ContactUs(
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
        return redirect('home')
        
    return render(request,'core/contact.html')
