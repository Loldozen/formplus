from django.db import models
import uuid
import random
import string
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _

# Create your models here.

class Product(models.Model):


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=255)
    prod_id = models.CharField(max_length=15)
    category = models.CharField(max_length=255)
    description = models.TextField(null=True)
    owner = models.CharField(max_length=250) # should be a ManyToOne relationship to the vendor model but that is out of scope
    # image_link = ArrayField(models.TextField(), null=True) # multiple product images but out of scope

    created_datetime = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_datetime = models.DateTimeField(_('Last update at'), auto_now=True)
    is_deleted = models.BooleanField(default=False)
    objects = models.Manager()

    def __str__(self):
        """Representation of products."""

        return 'Product - {} '.format(self.name)

    def soft_delete(self):
        self.is_deleted = True
        self.save()
    
    def generate_product_id(self):
        letters_and_digits = string.ascii_letters + string.digits
        result_str = ''.join((random.choice(letters_and_digits) for i in range(6)))
        result = 'PRD-{}'.format(result_str)
        return result
    

class Variation(models.Model):
    """
    Represent different variants of the product, size, color, pricing etc
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    var_id = models.CharField(max_length=15)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    type = models.CharField(max_length=255) # variation type e.g color, size etc
    value = models.CharField(max_length=255)
    price = models.CharField(max_length=20)
    quantity = models.IntegerField(default=1)
    number_in_stock = models.IntegerField(default=0)

    def __str__(self):
        """Representation of product labels."""

        return '{} - Variant'.format(self.type)

    def generate_variation_id(self):
        letters_and_digits = string.ascii_letters + string.digits
        result_str = ''.join((random.choice(letters_and_digits) for i in range(6)))
        result = 'VAR-{}'.format(result_str)
        return result

class Order(models.Model):

    CARTED = 0
    PAID = 1
    COMPLETED = 2
    CANCELLED = 3

    ORDER_STATE = (
        (CARTED, 'CARTED'),
        (PAID, 'PAID'),
        (COMPLETED, 'COMPLETED'),
        (CANCELLED, 'CANCELLED')
    )

    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    order_id = models.CharField(max_length=15)
    owner = models.CharField(max_length=250) # should be a ManyToOne relationship to the user model but that is out of scope
    variation_and_quantity = models.JSONField()
    total_amount = models.CharField(max_length=20)
    order_state = models.IntegerField(choices=ORDER_STATE)
    payment_reference = models.CharField(max_length=255, null=True)
    created_datetime = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_datetime = models.DateTimeField(_('Last update at'), auto_now=True)
    is_deleted = models.BooleanField(default=False)

    objects = models.Manager()

    def soft_delete(self):
        self.is_deleted = True
        self.save()


    def __str__(self):
        """Representation of products orders."""

        return 'Order for {}'.format(self.owner)

    def generate_order_id(self):
        letters_and_digits = string.ascii_letters + string.digits
        result_str = ''.join((random.choice(letters_and_digits) for i in range(6)))
        result = 'ORD-{}'.format(result_str)
        return result
    
    def get_order_state(self):
        if self.order_state == 0:
            return 'Carted'
        elif self.order_state == 1:
            return 'Paid'
        elif self.order_state == 2:
            return 'Completed'
        elif self.order_state == 3:
            return 'Cancelled'
        else:
            return 'Invalid data' 