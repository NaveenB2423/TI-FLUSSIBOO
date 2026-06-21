from django.shortcuts import render, HttpResponse, redirect
from django.http.response import JsonResponse
from domain.models import Category, Product, Size, Color, ProductVariant, Cart, SubMenus, MainMenus

def add_product(request):
    categories = MainMenus.objects.filter(status=1).all()
    sizes = Size.objects.filter(status=1).all()
    colors = Color.objects.filter(status=1).all()
    product = Product()
    if request.method == "POST":
        product.name= request.POST.get('name','').strip()
        product.description = request.POST.get('description','').strip()
        product.main_menu_id = request.POST.get('category')
        if request.POST.get('subcategory'):
            product.sub_menu_id = request.POST.get('subcategory')
        product.price = request.POST.get('price','').strip()
        product.discount_price = request.POST.get('discount_price','').strip()
        product.image = request.FILES.get('itemImage', '')
        product.save()
        
        selected_colors = request.POST.getlist('color')
        selected_sizes = request.POST.getlist('size')
        for color_id in selected_colors:
            
            for size_id in selected_sizes:
                product_sku = ProductVariant()
                product_sku.color = Color.objects.get(id=color_id)
                product_sku.size = Size.objects.get(id=size_id)
                product_sku.product = product
                product_sku.save()

    return render(request, 'product/add_product.html', {'categories':categories,'sizes':sizes,'colors':colors})

def list_product(request):
    products = Product.objects.filter(status=1).all()
    return render(request, 'product/list_product.html',{'products': products})

def edit_product(request,id):
    categories = MainMenus.objects.filter(status=1).all
    sizes = Size.objects.filter(status=1).all()
    colors = Color.objects.filter(status=1).all()
    product = Product.objects.get(id=id)
    if request.method == "POST":
        product.name= request.POST.get('name','').strip()
        product.description = request.POST.get('description','').strip()
        product.main_menu_id = request.POST.get('category')
        product.price = request.POST.get('price','').strip()
        product.discount_price = request.POST.get('discount_price','').strip()
        if request.FILES.get('itemImage'):
            product.image = request.FILES.get('itemImage', '')
        product.save()
        
        selected_colors = request.POST.getlist('color')
        selected_sizes = request.POST.getlist('size')
        old_variants = ProductVariant.objects.filter(product=product).all()
        for old in old_variants:
            old.status=0
            old.save()
        for color_id in selected_colors: 
            for size_id in selected_sizes:
                color = Color.objects.get(id=color_id)
                size = Size.objects.get(id=size_id)
                check_variant = ProductVariant.objects.filter(product=product, color=color,size=size).exists()
                if not check_variant:
                    variant = ProductVariant.objects.create(product=product, size=size, color=color,status=1)
                else:
                    variant = ProductVariant.objects.get(product=product, color=color,size=size)
                    variant.status=1
                    variant.save()

        return redirect(list_product)
    return render(request, 'product/edit_product.html',{'product': product,'categories':categories,'sizes':sizes,'colors':colors})

def update_home_item(request):
    id =  request.POST.get('id')
    data_id = request.POST.get('data_id') if request.POST.get('data_id') else  None
    return JsonResponse({"status" : "success"})

def delete_product(request,id):
    product = Product.objects.get(id=id)
    product.status = 0
    product.save()
    return redirect(list_product)

def ecommerce(request):
    product = Product.objects.filter(status=1).last()
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        size_name = request.POST.get('size')
        
        color_name =request.POST.get('color')
       
        qty =request.POST.get('qty')
        size = Size.objects.get(name=size_name,status=1)
        color = Color.objects.get(name=color_name,status=1)
        productVariant = ProductVariant.objects.get(product_id=product_id, size=size, color=color)
        cart = Cart()
        cart.variant=productVariant
        cart.qty = qty
        cart.save()
        
    return render(request,'product/e-commerce.html',{'product':product})

def get_sub_menus(request):
    if request.method == "POST":
        id = request.POST.get('id','').strip()
        sub_menus = SubMenus.objects.filter(main_menu_id=id).values()
        return JsonResponse({"values":list(sub_menus)})
    return JsonResponse({})