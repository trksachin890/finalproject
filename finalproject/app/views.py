from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.
def BASE(request):
    return render(request,'core/base.html')

def INDEX(request):
    return render(request,'core/index.html')

from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

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




from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

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
