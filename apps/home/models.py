import re
from datetime import date

from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import models

# Create your models here.
from django.utils.translation import gettext_lazy as _

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.timezone import now


# class CustomUser(AbstractUser):
#     user_type_choices=((1,"Manufacturer"),(2,"Customer"))
#     user_type=models.CharField(max_length=255,choices=user_type_choices,default=1)

def default_account_year_from():
    return date(date.today().year, 4, 1)


def default_account_year_upto():
    return date(date.today().year + 1, 3, 31)


def validate_gstin(value):
    pattern = re.compile(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$')
    if not pattern.match(value):
        raise ValidationError(
            _('%(value)s is not a valid GSTIN'),
            params={'value': value},
        )


class CompanyProfile(models.Model):
    COMPANY_TYPE = [('proprietorship', 'Proprietorship'),
                    ('partnership', 'Partnership'),
                    ('pvt_ltd', 'Pvt Ltd'),
                    ('public_ltd', 'Public Ltd'),
                    ('institution', 'Institution')]
    BUSINESS_TYPE = [('manufacturing', 'Manufacturing'),
                     ('trading', 'Trading'),
                     ('manufacturing_and_trading', 'Manufacturing & Trading'),
                     ('others', 'Others')]
    company_name = models.CharField(unique=True, max_length=30, null=True, blank=True)
    sh_name = models.CharField(max_length=30, null=True, blank=True)
    print_name = models.CharField(max_length=30, null=True, blank=True)
    address = models.TextField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    gstin = models.CharField(max_length=15, validators=[validate_gstin])
    company_type = models.CharField(choices=COMPANY_TYPE, max_length=30, default='proprietorship')
    business_type = models.CharField(choices=BUSINESS_TYPE, max_length=30, default='manufacturing')

    def __str__(self):
        return str(self.company_name)


class Account(models.Model):
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='accounts')
    account_year_from = models.DateField(verbose_name="Account Year From", default=default_account_year_from)
    account_year_upto = models.DateField(verbose_name="Account Year Upto", default=default_account_year_upto)
    books_from = models.DateField(verbose_name="Books From", default=default_account_year_from)

    def __str__(self):
        return f"Account for {self.company.company_name} from {self.account_year_from} to {self.account_year_upto}"


class GroupManager(models.Manager):
    def get_or_create_general_manufacturer(self):
        group, created = self.get_or_create(
            group_name__icontains='General Manufacturer',
            defaults={'group_name': 'General Manufacturer'}
        )
        return group


class ProductGroup(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    group_id = models.IntegerField(unique=True, null=True, blank=True)
    group_name = models.CharField(unique=True, max_length=30, null=True, blank=True)
    print_name = models.CharField(max_length=30, null=True, blank=True)
    sh_name = models.CharField(max_length=30, null=True, blank=True)
    code_name = models.CharField(max_length=30, null=True, blank=True)
    consolidation_code = models.CharField(max_length=30, null=True, blank=True)
    hsn_code = models.CharField(max_length=30, null=True, blank=True)
    gcr_code = models.CharField(max_length=30, null=True, blank=True)
    last_accessed = models.DateTimeField(default=now, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    objects = GroupManager()

    def __str__(self):
        return self.group_name

    class Meta:
        ordering = ['-id']
        db_table = 'ProductGroup'

    def save(self, *args, **kwargs):
        self.last_accessed = now()
        if not self.print_name or self.print_name is None:
            self.print_name = self.group_name
        super().save(*args, **kwargs)


class Manufacturer(models.Model):
    TYPE_CHOICES = [
        ('manufacturer', 'Manufacturer'),
        ('supplier', 'Supplier'),
    ]

    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    name = models.CharField(max_length=255, null=True, blank=True, unique=True)
    print_name = models.CharField(max_length=255, null=True, blank=True)
    sh_name = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(choices=TYPE_CHOICES, max_length=20, default='manufacturer')
    address = models.TextField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    contact = models.CharField(max_length=20, null=True, blank=True)
    last_accessed = models.DateTimeField(default=now, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']
        db_table = 'Manufacturer'

    def save(self, *args, **kwargs):
        self.last_accessed = now()
        if not self.print_name or self.print_name is None:
            self.print_name = self.name
        super().save(*args, **kwargs)


class Product(models.Model):
    STOCK_OPTION_CHOICE = [
        ('quantity_wise', 'Quantity Wise'),
        ('batch_wise', 'Batch Wise')
    ]
    TAX_CHOICE = [
        ('excluded', 'Excluded'),
        ('included', 'Included')
    ]
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    product_name = models.CharField(max_length=255, null=True, blank=True, unique=True)
    product_code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    print_name = models.CharField(max_length=255, null=True, blank=True)
    contact = models.CharField(max_length=20, null=True, blank=True)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, related_name='product_manufacturer')
    buy_rate = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    sell_rate = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    mrp = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    net_quantity = models.PositiveIntegerField(null=True, blank=True)
    stock_option = models.CharField(choices=STOCK_OPTION_CHOICE, max_length=20, default='quantity_wise')
    group = models.ForeignKey(ProductGroup, on_delete=models.CASCADE, related_name='product_group', null=True,
                              blank=True)
    last_accessed = models.DateTimeField(default=now, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.product_name} ({self.product_code})"

    class Meta:
        ordering = ['-id']
        db_table = 'Product'

    def save(self, *args, **kwargs):
        self.last_accessed = now()
        super().save(*args, **kwargs)


class Customer(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    customer_name = models.CharField(unique=True, max_length=30, null=True, blank=True)
    print_name = models.CharField(max_length=30, null=True, blank=True)
    sh_name = models.CharField(max_length=30, null=True, blank=True)
    contact = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    last_accessed = models.DateTimeField(default=now, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.customer_name}_({self.id})"

    class Meta:
        ordering = ['-id']
        db_table = 'Customer'

    def save(self, *args, **kwargs):
        self.last_accessed = now()
        if not self.print_name or self.print_name is None:
            self.print_name = self.customer_name
        super().save(*args, **kwargs)


class Receipt(models.Model):
    receipt_type = [('purchases', 'Purchases'),
                    ('adjustments', 'Adjustments'),
                    ('opening_stock', 'Opening Stock')]

    # receipt_status = [('received', 'Received'),
    #                   ('transit', 'Transit'),
    #                   ('approved', 'Approved'),
    #                   ('suspense', 'Suspense')]
    receipt_status = [
        ('purchases', [
            ('received', 'Received'),
            ('transit', 'Transit'),
            ('approved', 'Approved'),
            ('suspense', 'Suspense')
        ]),
        ('adjustments', [
            ('adjustment', 'Adjustment'),
            ('transfer', 'Transfer'),
            ('suspense', 'Suspense')
        ]),
        ('opening_stock', [
            ('none', 'None')
        ])
    ]
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    receipt_type = models.CharField(choices=receipt_type, max_length=20, default='purchases')
    receipt_status = models.CharField(choices=receipt_status, max_length=20, default='received')
    date = models.DateField(default=now)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT, related_name='receipt_manufacturers')
    # can do like Manufacturer.receipt_manufacturer.all()
    net_amount = models.DecimalField(decimal_places=2, max_digits=8, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.receipt_type}_({self.manufacturer.name})"

    class Meta:
        db_table = 'Receipt'


class ReceiptProduct(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name='receipt_models')
    # can do like Receipts.receipt_product.all()
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='receipt_products', null=True,
                                blank=True)
    quantity = models.PositiveIntegerField()
    discount = models.FloatField()

    def __str__(self):
        return f"{self.product.product_name}_({self.product.manufacturer.name})"

    class Meta:
        db_table = 'ReceiptProduct'
    # def clean(self):
    #     if self.product.manufacturer.id != self.receipt.manufacturer.id:
    #         raise ValidationError("The product must belong to the same manufacturer as the receipt.")
    #
    # def save(self,*args,**kwargs):
    #     self.discount = round(self.discount, 2)
    #     self.full_clean()
    #     super().save(*args,**kwargs)
