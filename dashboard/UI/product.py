from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from domain.models import Color, MainMenus, Product, ProductVariant, Size, SubMenus
from domain.validators import validate_image_file, validate_positive_number
from .decorators import admin_required


@admin_required
def add_product(request):
    categories = MainMenus.objects.filter(status=1)
    sizes = Size.objects.filter(status=1)
    colors = Color.objects.filter(status=1)

    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        category_id = request.POST.get('category')
        subcategory_id = request.POST.get('subcategory')
        raw_price = request.POST.get('price', '').strip()
        raw_discount_price = request.POST.get('discount_price', '').strip()
        uploaded_image = request.FILES.get('itemImage')
        selected_colors = request.POST.getlist('color')
        selected_sizes = request.POST.getlist('size')

        errors = []
        if not name:
            errors.append("Product name is required.")
        if not description:
            errors.append("Product description is required.")
        if not category_id:
            errors.append("Please select a category.")

        price = 0.0
        discount_price = 0.0
        try:
            price = validate_positive_number(raw_price, "Price")
        except ValidationError as e:
            errors.append(str(e.message))

        try:
            discount_price = validate_positive_number(raw_discount_price, "Discount price")
            if discount_price > price:
                errors.append("Discount price cannot exceed the original price.")
        except ValidationError as e:
            errors.append(str(e.message))

        if uploaded_image:
            try:
                validate_image_file(uploaded_image, max_size_mb=5)
            except ValidationError as e:
                errors.append(str(e.message))

        if not selected_colors:
            errors.append("Please select at least one color.")
        if not selected_sizes:
            errors.append("Please select at least one size.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'product/add_product.html', {
                'categories': categories,
                'sizes': sizes,
                'colors': colors,
            })

        try:
            category_obj = MainMenus.objects.get(id=category_id, status=1)
            subcategory_obj = None
            if subcategory_id:
                subcategory_obj = SubMenus.objects.filter(id=subcategory_id, status=1).first()

            product = Product.objects.create(
                name=name,
                description=description,
                main_menu=category_obj,
                sub_menu=subcategory_obj,
                price=price,
                discount_price=discount_price,
                image=uploaded_image,
                status=1,
            )

            for color_id in selected_colors:
                for size_id in selected_sizes:
                    try:
                        color = Color.objects.get(id=color_id, status=1)
                        size = Size.objects.get(id=size_id, status=1)
                        ProductVariant.objects.create(
                            product=product,
                            color=color,
                            size=size,
                            status=1,
                        )
                    except (Color.DoesNotExist, Size.DoesNotExist):
                        continue

            messages.success(request, f'Product "{name}" added successfully.')
            return redirect('list_product')

        except MainMenus.DoesNotExist:
            messages.error(request, "Selected category not found.")

    return render(request, 'product/add_product.html', {
        'categories': categories,
        'sizes': sizes,
        'colors': colors,
    })


@admin_required
def list_product(request):
    products = Product.objects.filter(status=1)
    return render(request, 'product/list_product.html', {'products': products})


@admin_required
def edit_product(request, id):
    categories = MainMenus.objects.filter(status=1)
    sizes = Size.objects.filter(status=1)
    colors = Color.objects.filter(status=1)
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        category_id = request.POST.get('category')
        raw_price = request.POST.get('price', '').strip()
        raw_discount_price = request.POST.get('discount_price', '').strip()
        uploaded_image = request.FILES.get('itemImage')
        selected_colors = request.POST.getlist('color')
        selected_sizes = request.POST.getlist('size')

        errors = []
        if not name:
            errors.append("Product name is required.")
        if not description:
            errors.append("Product description is required.")
        if not category_id:
            errors.append("Please select a category.")

        price = product.price
        discount_price = product.discount_price
        try:
            price = validate_positive_number(raw_price, "Price")
        except ValidationError as e:
            errors.append(str(e.message))

        try:
            discount_price = validate_positive_number(raw_discount_price, "Discount price")
            if discount_price > price:
                errors.append("Discount price cannot exceed the original price.")
        except ValidationError as e:
            errors.append(str(e.message))

        if uploaded_image:
            try:
                validate_image_file(uploaded_image, max_size_mb=5)
            except ValidationError as e:
                errors.append(str(e.message))

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'product/edit_product.html', {
                'product': product,
                'categories': categories,
                'sizes': sizes,
                'colors': colors,
            })

        try:
            product.name = name
            product.description = description
            product.main_menu = MainMenus.objects.get(id=category_id, status=1)
            product.price = price
            product.discount_price = discount_price
            if uploaded_image:
                product.image = uploaded_image
            product.save()

            if selected_colors and selected_sizes:
                ProductVariant.objects.filter(product=product).update(status=0)
                for color_id in selected_colors:
                    for size_id in selected_sizes:
                        try:
                            color = Color.objects.get(id=color_id)
                            size = Size.objects.get(id=size_id)
                            variant, _ = ProductVariant.objects.get_or_create(
                                product=product,
                                color=color,
                                size=size,
                            )
                            variant.status = 1
                            variant.save()
                        except (Color.DoesNotExist, Size.DoesNotExist):
                            continue

            messages.success(request, f'Product "{name}" updated successfully.')
            return redirect('list_product')

        except MainMenus.DoesNotExist:
            messages.error(request, "Selected category not found.")

    return render(request, 'product/edit_product.html', {
        'product': product,
        'categories': categories,
        'sizes': sizes,
        'colors': colors,
    })


@admin_required
def update_home_item(request):
    return JsonResponse({"status": "success"})


@admin_required
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    product.status = 0
    product.save()
    messages.success(request, f'Product "{product.name}" removed.')
    return redirect('list_product')


@admin_required
def ecommerce(request):
    product = Product.objects.filter(status=1).last()
    return render(request, 'product/e-commerce.html', {'product': product})


@admin_required
def get_sub_menus(request):
    if request.method == "POST":
        raw_id = request.POST.get('id', '').strip()
        try:
            menu_id = int(raw_id)
            sub_menus = list(SubMenus.objects.filter(main_menu_id=menu_id, status=1).values('id', 'name'))
            return JsonResponse({"values": sub_menus})
        except ValueError:
            return JsonResponse({"values": []}, status=400)
    return JsonResponse({"values": []})