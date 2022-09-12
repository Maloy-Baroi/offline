from django.db import models

# Create your models here.
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile_user')
    full_name = models.CharField(max_length=264, blank=True, null=True)
    secondary_phone_number = models.CharField(max_length=20)
    shop = models.CharField(max_length=20, blank=True, null=True)


class CategoryModel(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"


class ProductModel(models.Model):
    product_name = models.CharField(max_length=200)
    category_name = models.ForeignKey(CategoryModel, on_delete=models.CASCADE, related_name='product_category')
    No_of_available = models.IntegerField()
    price_per_unit = models.FloatField()
    product_details = models.TextField()
    image = models.ImageField(upload_to='product_image/')

    def __str__(self):
        return f"{self.product_name}"


class ShortageOfProduct(models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, related_name='shortage_product')
    storageAmount = models.IntegerField()


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_user')
    item = models.ForeignKey(ProductModel, on_delete=models.CASCADE, related_name='item')
    quantity = models.IntegerField(default=0)
    purchased = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.quantity} x {self.item.product_name}'

    def get_total(self):
        total = float(self.item.price_per_unit * self.quantity)
        return format(total, '0.2f')


status_choice = (
    ('Processing', 'Processing'),
    ('Confirmed', 'Confirmed'),
    ('Rejected', 'Rejected'),
    ('Completed', 'Completed'),
)


class Order(models.Model):
    order_items = models.ManyToManyField(Cart)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='order')
    ordered = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    payment_id = models.CharField(max_length=264, blank=True, null=True)
    order_id = models.CharField(max_length=264, blank=True, null=True)
    status = models.CharField(max_length=50, default="Processing", choices=status_choice)
    total_price = models.PositiveIntegerField(blank=True, null=True)

    def get_order_total(self):
        total = 0
        for i in self.order_items.all():
            total += i.quantity * i.item.price_per_unit
        return format(total, '0.2f')


class BillingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='billing_profile')
    phone_number = models.CharField(max_length=50, blank=True)
    shop_address = models.CharField(max_length=200, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    city_zone = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=70)

    def __str__(self):
        return f"{self.user} billing address"

    def is_full_filled(self):
        fields_name = [f.name for f in self._meta.get_fields()]

        for field in fields_name:
            value = getattr(self, field)
            if value is None or value == "":
                return False
        return True

    class Meta:
        verbose_name_plural = 'BillingAddresses'
