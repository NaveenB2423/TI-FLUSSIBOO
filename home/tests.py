from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from domain.models import User, MainMenus, Category, Color, Size, Product, ProductVariant, Cart
from domain.validators import (
    validate_mobile_number,
    validate_image_file,
    validate_positive_number,
    validate_quantity,
)


class ValidatorsTestCase(TestCase):
    def test_valid_mobile_numbers(self):
        self.assertEqual(validate_mobile_number("9876543210"), "9876543210")
        self.assertEqual(validate_mobile_number("+919876543210"), "+919876543210")

    def test_invalid_mobile_numbers(self):
        with self.assertRaises(ValidationError):
            validate_mobile_number("123")
        with self.assertRaises(ValidationError):
            validate_mobile_number("abc1234567")
        with self.assertRaises(ValidationError):
            validate_mobile_number("")

    def test_positive_number_validator(self):
        self.assertEqual(validate_positive_number("100.50"), 100.50)
        self.assertEqual(validate_positive_number(0), 0.0)
        with self.assertRaises(ValidationError):
            validate_positive_number("-5")
        with self.assertRaises(ValidationError):
            validate_positive_number("invalid")

    def test_quantity_validator(self):
        self.assertEqual(validate_quantity("5"), 5)
        with self.assertRaises(ValidationError):
            validate_quantity("0")
        with self.assertRaises(ValidationError):
            validate_quantity("500")
        with self.assertRaises(ValidationError):
            validate_quantity("abc")

    def test_image_file_validator(self):
        valid_img = SimpleUploadedFile("test.jpg", b"fake image content", content_type="image/jpeg")
        self.assertIsNotNone(validate_image_file(valid_img))

        invalid_file = SimpleUploadedFile("script.py", b"print('hack')", content_type="text/x-python")
        with self.assertRaises(ValidationError):
            validate_image_file(invalid_file)


class SecurityAndAccessTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.regular_user, _ = User.objects.get_or_create(
            mobile_no="9876543210",
            defaults={
                "first_name": "Customer",
                "role": "Customer",
                "is_admin": False,
            }
        )
        self.admin_user, _ = User.objects.get_or_create(
            mobile_no="9999999999",
            defaults={
                "first_name": "Admin",
                "role": "Admin",
                "is_admin": True,
            }
        )

    def test_unauthenticated_dashboard_redirects(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('admin_login'), response.url)

    def test_regular_user_cannot_access_dashboard(self):
        self.client.force_login(self.regular_user)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('admin_login'), response.url)

    def test_admin_user_can_access_dashboard(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_cart_access_requires_login(self):
        response = self.client.get(reverse('shopping_cart'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('customer_login'), response.url)


class CustomerSignupValidationTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_signup_invalid_mobile(self):
        response = self.client.post(reverse('customer_signup'), {
            'firstname': 'John',
            'mobile': '12345',
            'email': 'john@example.com',
            'password': 'password123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='john@example.com').exists())

    def test_signup_short_password(self):
        response = self.client.post(reverse('customer_signup'), {
            'firstname': 'John',
            'mobile': '9876543211',
            'email': 'john@example.com',
            'password': '123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(mobile_no='9876543211').exists())

    def test_signup_successful(self):
        response = self.client.post(reverse('customer_signup'), {
            'firstname': 'ValidUser',
            'mobile': '9876543212',
            'email': 'valid@example.com',
            'password': 'strongpassword123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(mobile_no='9876543212').exists())
