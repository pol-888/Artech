from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    position = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} Profile"

class Order(models.Model):
    customer_name = models.CharField(max_length=255)
    received_date = models.DateField()
    order_type = models.CharField(max_length=255)
    due_date = models.DateField()
    address = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=50)
    payment_type = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    description = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    image = models.ImageField(upload_to='order_images/', blank=True, null=True)

    def __str__(self):
        return f"Order for {self.customer_name} - {self.order_type}"
