from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
# Create your models here.

class User(AbstractUser):
    pass

class Product(models.Model):
    name = models.CharField(max_length = 200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10,decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to="products/", blank=True, null = True)

    @property # Use of @property makes it behave as an attribute . 
    # Thus making it simpler. Not to be used if the function consists of some parameters.
    def in_stock(self):
        return self.stock > 0
    
    def __str__(self):
        return self.name
    

class Order(models.Model):
    class StatusChoices(models.TextChoices): # using the concept of encapsulation. 
        # Makes it more clear and scoped to the Order class only (not public). Improves readability.
        PENDING = 'Pending'
        CONFIRMED = 'Confirmed'
        CANCELLED = 'Cancelled'

    order_id = models.UUIDField(primary_key=True,default=uuid.uuid4)
    # UUID stands for Universally Unique Identifier.

    # It’s a 128-bit number used to uniquely identify information in computer systems.

    # Represented as a 36-character string, typically like: 550e8400-e29b-41d4-a716-446655440000
    # uuid.uuid4 --> version 4 .
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default = StatusChoices.PENDING,
                              )

    products = models.ManyToManyField(Product,through="OrderItem",related_name="orders")
    # an order can have many products . likewise a product can be appear in many orders. Thus many-to-many and the
    # relationship is linked by a OrderItem class Table . This ensures changes and extra fields can be included such as
    # quantity and many more . Better way of defining the many to many relationship

    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, 
                              on_delete=models.CASCADE,
                              related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()


    @property
    def item_subtotal(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in order {self.order.order_id}"