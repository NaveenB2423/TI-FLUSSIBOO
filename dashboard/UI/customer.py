import logging
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import redirect, render

from domain.models import Customizedesgin, User, UserAddrsss
from domain.validators import validate_mobile_number
from .decorators import admin_required

logger = logging.getLogger(__name__)


@admin_required
def add_customer(request):
    if request.method == "POST":
        first_name = request.POST.get("frist_name", '').strip()
        last_name = request.POST.get("last_name", '').strip()
        email = request.POST.get("email", '').strip()
        mobile_no = request.POST.get("mobile_no", '').strip()
        password = request.POST.get("password", '').strip()
        role = request.POST.get("role", 'Customer').strip()

        address = request.POST.get("address", '').strip()
        state = request.POST.get("state", '').strip()
        city = request.POST.get("city", '').strip()
        pincode = request.POST.get("pincode", '').strip()

        errors = []
        if not first_name:
            errors.append("First name is required.")

        if not mobile_no:
            errors.append("Mobile number is required.")
        else:
            try:
                mobile_no = validate_mobile_number(mobile_no)
                if User.objects.filter(mobile_no=mobile_no).exists():
                    errors.append("A customer with this mobile number already exists.")
            except ValidationError as e:
                errors.append(str(e.message))

        if email:
            try:
                validate_email(email)
                if User.objects.filter(email__iexact=email).exists():
                    errors.append("A customer with this email already exists.")
            except ValidationError:
                errors.append("Invalid email format.")

        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters long.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'customers/add_customer.html')

        try:
            customer = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email if email else None,
                mobile_no=mobile_no,
                role=role if role else 'Customer',
                password=make_password(password),
                is_password_set=True,
                is_details_added=True if address else False,
            )

            if address or city or state or pincode:
                UserAddrsss.objects.create(
                    user=customer,
                    address=address,
                    state=state,
                    city=city,
                    pincode=pincode,
                    status=1,
                )

            messages.success(request, f'Customer "{first_name}" created successfully.')
            return redirect('listcustomer')

        except Exception:
            logger.exception("Failed to add customer")
            messages.error(request, "An unexpected error occurred while saving customer.")

    return render(request, 'customers/add_customer.html')


@admin_required
def view_customer(request):
    user_data = User.objects.filter(role="Customer")
    return render(request, 'customers/list_customers.html', {'user_data': user_data})


@admin_required
def view_design(request):
    data = Customizedesgin.objects.all().order_by('-id')
    return render(request, "custom_design.html", {'data': data})