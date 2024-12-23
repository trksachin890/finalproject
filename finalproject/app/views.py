from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate,logout
from django.contrib import messages
from app.models import *
from django.contrib.auth.decorators import login_required

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


def SingleProductImage(request):
    return  render(request,'core/single-product.html')


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
