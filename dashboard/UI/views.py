from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from domain.models import Image

def admin_login(request):
    if request.method == 'POST':
        mobile_no = request.POST.get('mobile_no', '')
        password = request.POST.get('password', '')
        user = authenticate(request,mobile_no=mobile_no, password=password)
        if user and user.is_active:
            login(request, user) 
            return redirect(dashboard)
        else:
            return render(request, 'admin_page/login.html', {'message' : "Invalid Credentials"})
    return render(request, 'admin_page/login.html')


def dashboard(request):
    return render(request,'forms.html')

def image(request):
    image = Image()
    if request.method == "POST":
        image.name = request.POST.get('name','')
        image.image = request.FILES.get('itemImage','')
        image.describe = request.POST.get('Category','')
        image.save()
    return render(request,'Image/add_image.html')
def get_image(request):
    images = Image.objects.all()
    return render(request,'Image/view_image.html',{'images':images})
def delete_image(request,id):
    image = Image.objects.get(id=id)
    image.delete()
    return redirect('get_image')