from django.shortcuts import render

# Create your views here.
def BASE(request):
    return render(request,'core/base.html')

def INDEX(request):
    return render(request,'core/index.html')
