import os
import re
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


def validate_mobile_number(value):
    """
    Validate and clean mobile numbers (allowing spaces, hyphens, parentheses).
    """
    if not value:
        raise ValidationError("Mobile number is required.")
    
    raw = str(value).strip()
    cleaned = re.sub(r'[\s\-\(\)]', '', raw)
    if not re.fullmatch(r'^\+?[0-9]{10,15}$', cleaned):
        raise ValidationError("Enter a valid mobile number (10 to 15 digits).")
    return cleaned


def validate_image_file(file, max_size_mb=5):
    """
    Validate that an uploaded file is a valid image type (jpg, jpeg, png, webp)
    and does not exceed the specified maximum size in megabytes.
    """
    if not file:
        return None

    # Check file size
    max_size_bytes = max_size_mb * 1024 * 1024
    if file.size > max_size_bytes:
        raise ValidationError(f"Image file size must not exceed {max_size_mb} MB.")

    # Check file extension
    ext = os.path.splitext(file.name)[1].lower()
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    if ext not in allowed_extensions:
        raise ValidationError(
            f"Unsupported file format '{ext}'. Allowed formats: {', '.join(allowed_extensions)}."
        )

    # Check content type if available
    content_type = getattr(file, 'content_type', '')
    if content_type:
        allowed_content_types = ['image/jpeg', 'image/png', 'image/webp', 'image/pjpeg']
        if content_type.lower() not in allowed_content_types:
            raise ValidationError("Uploaded file is not a valid image.")

    return file


def validate_positive_number(value, field_name="Price"):
    """
    Ensure the number is a positive float or int.
    """
    try:
        val = float(value)
        if val < 0:
            raise ValidationError(f"{field_name} must be greater than or equal to 0.")
        return val
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid value for {field_name}. Must be a valid number.")


def validate_quantity(value, min_val=1, max_val=100):
    """
    Ensure the quantity is a positive integer within the allowed bounds.
    """
    try:
        qty = int(value)
        if qty < min_val or qty > max_val:
            raise ValidationError(f"Quantity must be between {min_val} and {max_val}.")
        return qty
    except (ValueError, TypeError):
        raise ValidationError("Quantity must be a valid whole number.")
