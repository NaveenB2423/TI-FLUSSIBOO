from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class MyUserManager(BaseUserManager):
    def create_user(self, mobile_no, password=None):
        if not mobile_no:
            raise ValueError('Users must have an Mobile No')

        user = self.model(
            mobile_no=mobile_no,

        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile_no, password):
     
        user = self.create_user(
            mobile_no,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user
    

class User(AbstractBaseUser):
    role = models.CharField(max_length=50, null=True) 
    email = models.EmailField(verbose_name='email', max_length=100, null=True) 
    first_name = models.CharField(max_length=50, null=True) 
    last_name = models.CharField(max_length=50, null=True) 
    mobile_no = models.CharField(max_length=50, unique=True)
    is_details_added = models.BooleanField(default=False, null=True)
    is_password_set = models.BooleanField(default=False, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True, null=True)
    image = models.ImageField(upload_to= settings.USER_IMAGE_UPLOAD_PATH, null=True)  
    objects = MyUserManager()
    USERNAME_FIELD = 'mobile_no'
    REQUIRED_FIELDS = ['password']

    @property
    def mobile(self):
        return self.mobile_no

class UserAddrsss(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    type = models.CharField(max_length=200, null=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=50, null=True)
    state = models.CharField(max_length=50, null=True)
    pincode = models.CharField(max_length=50, null=True)
    status = models.SmallIntegerField(default=1, null=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_on = models.DateTimeField(auto_now=True, null=True)

class MainMenus(models.Model):
    name = models.CharField(max_length=100, null=False)  
    priority = models.SmallIntegerField(null=True)
    status = models.SmallIntegerField(default=1, null=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_on = models.DateTimeField(auto_now=True, null=True)
    
class SubMenus(models.Model):
    main_menu = models.ForeignKey(MainMenus, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=100, null=False) 
    status = models.SmallIntegerField(default=1, null=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_on = models.DateTimeField(auto_now=True, null=True)

class Category(models.Model):
    name = models.CharField(max_length=100, null=False)  
    priority = models.SmallIntegerField(null=True)
    status = models.SmallIntegerField(default=1, null=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_on = models.DateTimeField(auto_now=True, null=True)
    
class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=100, null=False)  
    status = models.SmallIntegerField(default=1, null=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_on = models.DateTimeField(auto_now=True, null=True)

class Color(models.Model):
    name = models.CharField(max_length=100, null=False)
    status = models.SmallIntegerField(default=1, null=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_on = models.DateTimeField(auto_now=True, null=True)

class Size(models.Model):
    name = models.CharField(max_length=100, null=False) 
    status = models.SmallIntegerField(default=1, null=True) 
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_on = models.DateTimeField(auto_now=True, null=True)

class Product(models.Model):
    name = models.CharField(max_length=200, null=False)
    description = models.CharField(max_length=1000)
    main_menu = models.ForeignKey(MainMenus, on_delete=models.CASCADE)
    sub_menu = models.ForeignKey(SubMenus, on_delete=models.CASCADE,null=True)
    price = models.FloatField(null=False)
    discount_price = models.FloatField(null=False)
    image = models.ImageField(
        upload_to=settings.PRODUCT_IMAGE_UPLOAD_PATH, null=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_on = models.DateTimeField(auto_now=True, null=True)
    status = models.SmallIntegerField(default=1, null=True)
    is_favorite = models.SmallIntegerField(default=0, null=True)

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    status = models.SmallIntegerField(null=True, default=1)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_on = models.DateTimeField(auto_now=True, null=True)

class Order(models.Model):
    generated_order_id = models.CharField(max_length=50, null=True)
    made_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=False)
    delivery_date = models.DateField(null=True)
    is_amount_paid = models.BooleanField(null=True)
    is_order_delivered = models.BooleanField(null=True, default=False)
    is_order_cancaled = models.BooleanField(null=True, default=False)
    status = models.SmallIntegerField(null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

class OrderItems(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=False)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    qty = models.SmallIntegerField(null=True)
    sub_total = models.FloatField(null=True, default=0.0)
    status = models.SmallIntegerField(null=True, default=1)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

class Cart(models.Model):
    made_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=False)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    qty = models.SmallIntegerField(null=True)
    status = models.SmallIntegerField(default=1, null=True)
    price = models.FloatField(null=True, default=0.0)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_on = models.DateTimeField(auto_now=True, null=True)

class TransactionDetails(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, null=False)
    generated_order_id = models.CharField(max_length=50, null=True)
    payment_type = models.CharField(
         max_length=10, null=True) 
    balance_amt_due = models.FloatField(null=True, default=0.0)
    original_amount = models.FloatField(default=0.0)
    coupon_discount = models.FloatField(null=True, default=0.0)
    net_amount = models.FloatField(default=0.0)
    refund_amount = models.FloatField(null=True, default=0.0)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    paymtent_status = models.CharField(max_length=50, null=True, default="Paid")
    
class TransactionAmount(models.Model):
    transaction = models.ForeignKey(
        TransactionDetails, on_delete=models.CASCADE, null=True
    )
    generated_order_id = models.CharField(max_length=50, null=True)
    payment_type = models.CharField(
        max_length=10, null=True)  # advance, estimated
    payment_amount = models.CharField(max_length=50, null=True)
    payment_gateway = models.CharField(max_length=40, null=True)
    paytm_checksum = models.CharField(max_length=500, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
class PayTMTransactionDetails(models.Model):
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING, null=True)
    transaction_for = models.ForeignKey(
        TransactionDetails, on_delete=models.DO_NOTHING, null=True
    )
    generated_order_id = models.CharField(max_length=50, null=True)
    payment_type = models.CharField(
        max_length=10, null=True)  # advance, estimated
    payment_amount = models.CharField(max_length=50, null=True)
    token = models.CharField(max_length=500, null=True)
    bank_name = models.CharField(max_length=500, null=True)
    bank_txn_id = models.CharField(max_length=500, null=True)
    checksum = models.CharField(max_length=500, null=True)
    currency = models.CharField(max_length=50, null=True)
    gateway_name = models.CharField(max_length=50, null=True)
    mid = models.CharField(max_length=100, null=True)
    payment_mode = models.CharField(max_length=50, null=True)
    response_code = models.CharField(max_length=50, null=True)
    response_msg = models.CharField(max_length=50, null=True)
    status = models.CharField(max_length=20, null=True)
    txn_amount = models.CharField(max_length=50, null=True)
    txn_date = models.DateTimeField(null=True)
    txn_id = models.CharField(max_length=500, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

class CustomerReview(models.Model):
    prodcut = models.ForeignKey(Product, on_delete=models.DO_NOTHING, null=True)
    rating = models.SmallIntegerField(null=True)
    review = models.CharField(max_length=500, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

class Customizedesgin(models.Model):
    Customername = models.CharField(max_length=100,null=True)
    moblie_no= models.CharField(max_length=100,null=True)
    email = models.EmailField(max_length=100,null=True)
    color = models.ForeignKey(Color, on_delete=models.CASCADE,null=True)
    size = models.ForeignKey(Size, on_delete=models.CASCADE,null=True)
    attachment = models.ImageField(
        upload_to=settings.CUSTOMIZE_IMAGE_UPLOAD_PATH, null=True)
    describe = models.CharField(max_length=500,null=True)

class Image(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200,null=True)
    image = models.ImageField(upload_to=settings.BANNER_IMAGE_UPLOAD_PATH, null=True)
    describe = models.CharField(max_length=200,null=True)