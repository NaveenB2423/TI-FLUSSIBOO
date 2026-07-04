import razorpay
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import HttpResponse, redirect, render

from domain.models import (
    Cart,
    Color,
    Customizedesgin,
    Image,
    MainMenus,
    Product,
    ProductVariant,
    Size,
    User,
)


def index(request):
    menus = MainMenus.objects.filter(status=1).order_by('priority')
    image = Image.objects.filter(describe = "Printed T-Shits")
    women_image = Image.objects.filter(describe = "For Women")
    men_image = Image.objects.filter(describe = "For Men")
    context ={
        'menus':menus,
        'image':image,
        'women_image':women_image,
        'men_image':men_image
    }
    return render(request, 'home/index.html',context)  

def main_products(request, menu):
    products = Product.objects.filter(main_menu__name__iexact=menu)
    if not products.exists():
        return HttpResponse(f"No products found for {menu}")
    return render(request, 'home/selected-products.html', {'current_url': menu, 'products': products})

def sub_products(request, main_menu, sub_menu):
    products = Product.objects.filter(main_menu__name__iexact=main_menu, sub_menu__name__iexact=sub_menu)
    if not products.exists():
        return HttpResponse(f"No products found for {main_menu} / {sub_menu}")
    return render(request, 'home/selected-products.html', {'current_url': main_menu, 'products': products})

def about_us(request):
    return render(request,'home/about.html')

def contact_us(request):
    return render(request,'home/contact.html')

def customer_login(request):

    if request.method == 'POST':
        mobile = request.POST.get('mobile', '')
        password = request.POST.get('password', '')
        
        user = authenticate(request,mobile_no=mobile, password=password)

        if user and user.is_active:
            login(request, user)
            messages.success(request, "Welcome back! You are now logged in.")
            return redirect('index')
        else:
            messages.error(request, "Invalid mobile number or password. Please try again.")
            return redirect('customer_login')


    return render(request,'home/login.html')

def customer_logout(request):
    logout(request)
    return redirect('/')

def customer_signup(request):
    if request.method == 'POST':
       new_user =  User()
       new_user.first_name = request.POST.get('firstname','').strip()
       new_user.mobile_no = request.POST.get('mobile','').strip()
       new_user.email = request.POST.get('email','').strip()
       new_user.password = make_password(request.POST.get('password','').strip())
       new_user.is_password_set =1
       new_user.save()
       messages.success(request, "Account created successfully. Please login to continue.")
       return redirect('customer_login')
    return render(request,'home/signup.html')

def products(request):
    products = Product.objects.all()
    distinct_sizes = Size.objects.filter(
        productvariant__product__in=products
    ).distinct()

    return render(request, 'home/product.html', {
        "product": products,
        "distinct_sizes": distinct_sizes
    })

def product_details(request,name):
    original_name = name.replace("-"," ")
    product = Product.objects.filter(name__iexact=original_name).last()
    if request.method == 'POST':
        if request.user.is_authenticated:
            product_id = request.POST.get('product_id')
            size_name = request.POST.get('size')
            color_name =request.POST.get('color')
            qty =request.POST.get('qty')
            size = Size.objects.get(name=size_name,status=1)
            color = Color.objects.get(name=color_name,status=1)
            productVariant = ProductVariant.objects.get(product_id=product_id, size=size, color=color)
            cart = Cart()
            cart.made_by=request.user
            cart.variant=productVariant
            cart.qty = qty
            cart.price=product.discount_price * float(qty)
            cart.save()
            messages.success(request, f"{product.name} added to your cart.")
            return redirect('product_details', name=name)
        else:
            messages.error(request, "Please login to add items to your cart.")
            return redirect('customer_login')
    return render(request,'home/product-details.html',{'product':product})

def shopping_cart(request):
    if request.user.is_authenticated:
        carts = Cart.objects.filter(made_by=request.user)
        total_amount = carts.aggregate(Sum('price'))['price__sum']
    else:
        messages.error(request, "Please login to view your cart.")
        return redirect('customer_login')
    return render(request,'home/shopping-cart.html',{'carts':carts,'total_amount':total_amount})


def update_cart(request):
    if request.method == 'POST':
        cart_id = request.POST.get('cart_id')
        qty = int(request.POST.get('qty'))

        # Get the cart item and update the quantity
        cart = Cart.objects.get(id=cart_id, made_by=request.user)
        cart.qty = qty
        cart.save()

        # Recalculate the total for this cart item
        item_total = cart.qty * cart.variant.product.discount_price
        
        # Recalculate the total amount for the cart
        total_amount = Cart.objects.filter(made_by=request.user).aggregate(Sum('price'))['price__sum']

        return JsonResponse({
            'total_amount': total_amount,
            'item_total': item_total
        })

def delete_cart(request):
    if request.method == 'POST':
        cart_id = request.POST.get('cart_id')
        try:
            cart_item = Cart.objects.get(id=cart_id, made_by=request.user)
            product_name = cart_item.variant.product.name
            cart_item.delete()
            messages.success(request, f'"{product_name}" has been removed from your cart.')
        except Cart.DoesNotExist:
            messages.error(request, 'Item not found in your cart.')
    return redirect('shopping_cart')

def blog(request):
    return render(request,'home/blog.html')

def blog_details(request):
    return render(request,'home/blog-details.html')

def cart(request):
    if not request.user.is_authenticated:
        messages.error(request, "Please login to view your cart.")
        return redirect('customer_login')
    carts = Cart.objects.filter(made_by=request.user)
    total_amount = carts.aggregate(Sum('price'))['price__sum'] or 0
    return render(request,'home/pay-cart.html',{'carts':carts,'total_amount':total_amount})

def custompage(request):
    sizes = Size.objects.filter(status=1).all()
    colors = Color.objects.filter(status=1).all()
    
    if request.method == 'POST':
        customize = Customizedesgin()
        customize.Customername = request.POST.get('name', '').strip()
        customize.moblie_no = request.POST.get('mobile_no', '').strip()
        customize.email = request.POST.get('email', '').strip()

        size_id = request.POST.get('size', '').strip()
        color_id = request.POST.get('color', '').strip()
        try:
            customize.size = Size.objects.get(id=size_id)
            customize.color = Color.objects.get(id=color_id)
        except Size.DoesNotExist:
            return HttpResponse("Size not found.", status=400)
        except Color.DoesNotExist:
            return HttpResponse("Color not found.", status=400)
        
        customize.attachment = request.FILES.get('design_image')
        customize.describe = request.POST.get('describe', '').strip()
        customize.save()
    context ={
        'size':sizes,
        'color':colors
    }
    return render(request,'home/Custom-page.html',context)

# views.py


def create_order(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "login required"}, status=401)

    carts = Cart.objects.filter(made_by=request.user)
    total_amount = carts.aggregate(Sum('price'))['price__sum']

    if not total_amount:
        return JsonResponse({"error": "No items in cart"}, status=400)

    amount_in_paisa = int(total_amount * 100)     # Razorpay accepts paisa

    client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET ))

    # Create Razorpay Order
    order = client.order.create({
        "amount": amount_in_paisa,
        "currency": "INR",
        "payment_capture": 1
    })

    return JsonResponse({
        "order_id": order["id"],
        "amount": amount_in_paisa,
        "key": settings.RAZORPAY_API_KEY,
        "name": "Trendy Looms",
        "email": request.user.email,
    })

def payment_success(request):
    payment_id = request.GET.get('payment_id', '')
    if request.user.is_authenticated and payment_id:
        Cart.objects.filter(made_by=request.user).delete()
        messages.success(request, f'Payment successful! Payment ID: {payment_id}')
    return render(request, 'home/success.html')
