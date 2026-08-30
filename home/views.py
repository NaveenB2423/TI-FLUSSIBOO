import logging
import razorpay
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from domain.models import (
    Cart,
    Color,
    Customizedesgin,
    Image,
    MainMenus,
    Order,
    OrderItems,
    Product,
    ProductVariant,
    Size,
    SubMenus,
    TransactionDetails,
    User,
)
from domain.validators import (
    validate_image_file,
    validate_mobile_number,
    validate_quantity,
)

logger = logging.getLogger(__name__)


def index(request):
    menus = MainMenus.objects.filter(status=1).order_by('priority')
    image = Image.objects.filter(describe="Printed T-Shits")
    women_image = Image.objects.filter(describe="For Women")
    men_image = Image.objects.filter(describe="For Men")
    context = {
        'menus': menus,
        'image': image,
        'women_image': women_image,
        'men_image': men_image,
    }
    return render(request, 'home/index.html', context)


def main_products(request, menu):
    products = Product.objects.filter(main_menu__name__iexact=menu, status=1)
    return render(request, 'home/selected-products.html', {'current_url': menu, 'products': products})


def sub_products(request, main_menu, sub_menu):
    products = Product.objects.filter(
        main_menu__name__iexact=main_menu,
        sub_menu__name__iexact=sub_menu,
        status=1,
    )
    return render(request, 'home/selected-products.html', {'current_url': main_menu, 'products': products})


def about_us(request):
    return render(request, 'home/about.html')


def contact_us(request):
    return render(request, 'home/contact.html')


def customer_login(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        mobile = request.POST.get('mobile', '').strip()
        password = request.POST.get('password', '').strip()

        if not mobile or not password:
            messages.error(request, "Please enter both mobile number/email and password.")
            return render(request, 'home/login.html')

        user = None

        # 1. Allow login via Email
        if '@' in mobile:
            try:
                user_match = User.objects.filter(email__iexact=mobile).first()
                if user_match:
                    user = authenticate(request, mobile_no=user_match.mobile_no, password=password)
            except Exception:
                pass

        # 2. Allow login via Mobile Number (sanitized)
        if user is None:
            import re
            cleaned_mobile = re.sub(r'[\s\-\(\)]', '', mobile)
            user = authenticate(request, mobile_no=cleaned_mobile, password=password)
            
            # Try +91 / without +91 variations if not matched
            if user is None and cleaned_mobile.startswith('+91'):
                user = authenticate(request, mobile_no=cleaned_mobile[3:], password=password)
            elif user is None and not cleaned_mobile.startswith('+') and len(cleaned_mobile) == 10:
                user = authenticate(request, mobile_no='+91' + cleaned_mobile, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or 'User'}!")
                next_url = request.GET.get('next') or request.POST.get('next') or ''
                if next_url and next_url.startswith('/') and not next_url.startswith('//'):
                    return redirect(next_url)
                if getattr(user, 'is_admin', False):
                    return redirect('dashboard')
                return redirect('index')
            else:
                messages.error(request, "Your account has been deactivated. Please contact support.")
        else:
            messages.error(request, "Invalid mobile number/email or password. Please try again.")

        return render(request, 'home/login.html', {'mobile': mobile})


def customer_logout(request):
    logout(request)
    messages.success(
        request,
        "You have been logged out successfully.",
        extra_tags='logout',
    )
    return redirect('index')


def page_not_found(request, path=''):
    return render(request, 'home/404.html', status=404)


def custom_404(request, exception):
    return page_not_found(request)


def custom_500(request):
    return render(request, 'home/500.html', status=500)


def customer_signup(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        first_name = request.POST.get('firstname', '').strip()
        raw_mobile = request.POST.get('mobile', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        # Validation
        errors = []
        if not first_name:
            errors.append("Full name is required.")

        mobile = None
        if not raw_mobile:
            errors.append("Mobile number is required.")
        else:
            try:
                mobile = validate_mobile_number(raw_mobile)
                if User.objects.filter(mobile_no=mobile).exists():
                    errors.append("An account with this mobile number already exists.")
            except ValidationError as e:
                errors.append(str(e.message))

        if email:
            try:
                validate_email(email)
                if User.objects.filter(email__iexact=email).exists():
                    errors.append("An account with this email address already exists.")
            except ValidationError:
                errors.append("Please enter a valid email address.")

        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters long.")
        elif confirm_password and password != confirm_password:
            errors.append("Passwords do not match. Please ensure both fields are identical.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'home/signup.html', {
                'firstname': first_name,
                'mobile': raw_mobile,
                'email': email,
            })

        new_user = User()
        new_user.first_name = first_name
        new_user.mobile_no = mobile or raw_mobile
        new_user.email = email if email else None
        new_user.password = make_password(password)
        new_user.is_password_set = True
        new_user.role = 'Customer'
        new_user.save()

        messages.success(request, "Account created successfully! Please log in to continue.")
        return redirect('customer_login')

    return render(request, 'home/signup.html')


def products(request):
    product_list = Product.objects.filter(status=1)
    distinct_sizes = Size.objects.filter(
        productvariant__product__in=product_list,
        status=1,
    ).distinct()

    return render(request, 'home/product.html', {
        "product": product_list,
        "distinct_sizes": distinct_sizes,
    })


def product_details(request, name):
    original_name = name.replace("-", " ")
    product = Product.objects.filter(name__iexact=original_name, status=1).last()
    if not product:
        return page_not_found(request)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to add items to your cart.")
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")

        product_id = request.POST.get('product_id')
        size_name = request.POST.get('size', '').strip()
        color_name = request.POST.get('color', '').strip()
        raw_qty = request.POST.get('qty', 1)

        try:
            qty = validate_quantity(raw_qty, min_val=1, max_val=50)
        except ValidationError as e:
            messages.error(request, str(e.message))
            return render(request, 'home/product-details.html', {'product': product})

        try:
            size = Size.objects.get(name=size_name, status=1)
            color = Color.objects.get(name=color_name, status=1)
            product_variant = ProductVariant.objects.get(
                product_id=product_id,
                size=size,
                color=color,
                status=1,
            )
        except (Size.DoesNotExist, Color.DoesNotExist, ProductVariant.DoesNotExist):
            messages.error(request, "The selected size/color combination is not available.")
            return render(request, 'home/product-details.html', {'product': product})

        # Check existing cart item for this user & variant
        cart_item, created = Cart.objects.get_or_create(
            made_by=request.user,
            variant=product_variant,
            defaults={
                'qty': qty,
                'price': (product.discount_price if product.discount_price > 0 else product.price) * qty,
            }
        )
        if not created:
            cart_item.qty = min(cart_item.qty + qty, 100)
            cart_item.price = (product.discount_price if product.discount_price > 0 else product.price) * cart_item.qty
            cart_item.save()

        messages.success(request, f'"{product.name}" has been added to your cart.')
        return redirect('product_details', name=name)

    return render(request, 'home/product-details.html', {'product': product})


@login_required
def shopping_cart(request):
    carts = Cart.objects.filter(made_by=request.user)
    total_amount = carts.aggregate(Sum('price'))['price__sum'] or 0.0
    return render(request, 'home/shopping-cart.html', {'carts': carts, 'total_amount': total_amount})


@login_required
@require_POST
def update_cart(request):
    cart_id = request.POST.get('cart_id')
    raw_qty = request.POST.get('qty')

    try:
        qty = validate_quantity(raw_qty, min_val=1, max_val=100)
    except ValidationError as e:
        return JsonResponse({'error': str(e.message)}, status=400)

    try:
        cart_item = Cart.objects.get(id=cart_id, made_by=request.user)
    except Cart.DoesNotExist:
        return JsonResponse({'error': 'Cart item not found.'}, status=404)

    unit_price = (
        cart_item.variant.product.discount_price
        if cart_item.variant.product.discount_price > 0
        else cart_item.variant.product.price
    )
    cart_item.qty = qty
    cart_item.price = unit_price * qty
    cart_item.save()

    total_amount = Cart.objects.filter(made_by=request.user).aggregate(Sum('price'))['price__sum'] or 0.0

    return JsonResponse({
        'total_amount': round(total_amount, 2),
        'item_total': round(cart_item.price, 2),
    })


@login_required
@require_POST
def delete_cart(request):
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
    return render(request, 'home/blog.html')


def blog_details(request):
    return render(request, 'home/blog-details.html')


@login_required
def cart(request):
    carts = Cart.objects.filter(made_by=request.user)
    total_amount = carts.aggregate(Sum('price'))['price__sum'] or 0.0
    return render(request, 'home/pay-cart.html', {'carts': carts, 'total_amount': total_amount})


def custompage(request):
    sizes = Size.objects.filter(status=1)
    colors = Color.objects.filter(status=1)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        mobile = request.POST.get('mobile_no', '').strip()
        email = request.POST.get('email', '').strip()
        size_id = request.POST.get('size', '').strip()
        color_id = request.POST.get('color', '').strip()
        describe = request.POST.get('describe', '').strip()
        uploaded_image = request.FILES.get('design_image')

        errors = []
        if not name:
            errors.append("Customer name is required.")
        if not mobile:
            errors.append("Mobile number is required.")
        else:
            try:
                mobile = validate_mobile_number(mobile)
            except ValidationError as e:
                errors.append(str(e.message))

        if email:
            try:
                validate_email(email)
            except ValidationError:
                errors.append("Invalid email address.")

        size_obj = None
        color_obj = None
        if size_id:
            try:
                size_obj = Size.objects.get(id=size_id, status=1)
            except (Size.DoesNotExist, ValueError):
                errors.append("Selected size does not exist.")

        if color_id:
            try:
                color_obj = Color.objects.get(id=color_id, status=1)
            except (Color.DoesNotExist, ValueError):
                errors.append("Selected color does not exist.")

        if uploaded_image:
            try:
                validate_image_file(uploaded_image, max_size_mb=5)
            except ValidationError as e:
                errors.append(str(e.message))

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            customize = Customizedesgin(
                Customername=name,
                moblie_no=mobile,
                email=email if email else None,
                size=size_obj,
                color=color_obj,
                attachment=uploaded_image,
                describe=describe,
            )
            customize.save()
            messages.success(request, "Your customization request has been submitted successfully!")
            return redirect('custompage')

    context = {
        'size': sizes,
        'color': colors,
    }
    return render(request, 'home/Custom-page.html', context)


@login_required
def create_order(request):
    carts = Cart.objects.filter(made_by=request.user)
    if not carts.exists():
        return JsonResponse({"error": "No items in cart."}, status=400)

    # Calculate authoritative total directly on backend
    total_amount = sum(
        (c.variant.product.discount_price if c.variant.product.discount_price > 0 else c.variant.product.price) * c.qty
        for c in carts
    )
    if total_amount <= 0:
        return JsonResponse({"error": "Invalid order total."}, status=400)

    amount_in_paisa = int(round(total_amount * 100))

    if not getattr(settings, 'RAZORPAY_API_KEY', '') or not getattr(settings, 'RAZORPAY_API_SECRET', ''):
        logger.error("Razorpay API keys are not set in environment variables (RAZORPAY_API_KEY / RAZORPAY_API_SECRET).")
        return JsonResponse({"error": "Payment gateway is not configured. Please set RAZORPAY_API_KEY and RAZORPAY_API_SECRET."}, status=503)

    client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

    try:
        razorpay_order = client.order.create({
            "amount": amount_in_paisa,
            "currency": "INR",
            "payment_capture": 1,
        })
    except Exception as e:
        logger.exception("Failed to create Razorpay order")
        return JsonResponse({"error": "Failed to initiate payment gateway."}, status=500)

    # Persist Order and Transaction record
    order_record = Order.objects.create(
        generated_order_id=razorpay_order["id"],
        made_by=request.user,
        is_amount_paid=False,
        is_order_delivered=False,
        is_order_cancaled=False,
        status=1,
    )

    for item in carts:
        OrderItems.objects.create(
            order=order_record,
            variant=item.variant,
            qty=item.qty,
            sub_total=item.price,
            status=1,
        )

    TransactionDetails.objects.create(
        order=order_record,
        generated_order_id=razorpay_order["id"],
        payment_type="online",
        original_amount=total_amount,
        net_amount=total_amount,
        paymtent_status="Pending",
    )

    return JsonResponse({
        "order_id": razorpay_order["id"],
        "amount": amount_in_paisa,
        "key": settings.RAZORPAY_API_KEY,
        "name": "TI FLUSSIBOO",
        "email": request.user.email or "",
    })


@login_required
def payment_success(request):
    payment_id = request.POST.get('razorpay_payment_id') or request.GET.get('payment_id') or request.GET.get('razorpay_payment_id', '')
    order_id = request.POST.get('razorpay_order_id') or request.GET.get('order_id') or request.GET.get('razorpay_order_id', '')
    signature = request.POST.get('razorpay_signature') or request.GET.get('signature') or request.GET.get('razorpay_signature', '')

    if not payment_id:
        messages.error(request, "Invalid payment confirmation request.")
        return redirect('shopping_cart')

    # If signature and order_id are present, cryptographically verify signature
    if order_id and signature:
        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature,
            })
        except razorpay.errors.SignatureVerificationError:
            logger.warning("Razorpay signature verification failed for payment %s", payment_id)
            messages.error(request, "Payment verification failed. Please contact customer support.")
            return redirect('shopping_cart')

    # Update database records
    if order_id:
        Order.objects.filter(generated_order_id=order_id, made_by=request.user).update(
            is_amount_paid=True
        )
        TransactionDetails.objects.filter(generated_order_id=order_id).update(
            paymtent_status="Paid"
        )

    # Clear user's cart
    Cart.objects.filter(made_by=request.user).delete()
    messages.success(request, f"Payment successful! Transaction Reference: {payment_id}")
    return render(request, 'home/success.html', {'payment_id': payment_id})


def db_check(request):
    from django.db import connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        user_count = User.objects.count()
        db_engine = connection.settings_dict.get('ENGINE', 'unknown').split('.')[-1]
        
        return JsonResponse({
            "status": "connected",
            "database_engine": db_engine,
            "user_count": user_count,
            "connected": True
        })
    except Exception as e:
        logger.exception("Database diagnostic check failed")
        return JsonResponse({
            "status": "error",
            "error_details": str(e),
            "connected": False
        }, status=500)

