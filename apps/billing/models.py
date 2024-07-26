import re
from datetime import date

from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

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

# Create your models here.
class CustomUser(AbstractUser):
    class Meta:
        db_table = 'CustomUser'


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

class Location(models.Model):
    SALE_STATE_LIST = [('within_state', 'Within State'),
                       ('outside_state', 'Outside State'),
                       ('sale_nil_gst', 'Sale(NIL GST)')]

    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    address = models.TextField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.PositiveIntegerField(null=True, blank=True)
    state_name = models.CharField(max_length=50, null=True, blank=True)
    sale_state = models.CharField(choices=SALE_STATE_LIST, max_length=50, null=True, blank=True)
    state_code = models.CharField(max_length=2, null=True, blank=True)

    class Meta:
        ordering = ['-id']
        db_table = 'Location'

#add this manager after creation of company profile- no need for give select_related on every queryset
#give BaseManager for objects in model
# so that i can use objects manager and by default it fetches select_related..
class BaseManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('company_profile')



class GroupManager(models.Manager):
    def get_or_create_general_group(self):
        group, created = self.get_or_create(
            group_name__icontains='General Group',
            defaults={'group_name': 'General Group'}
        )
        return group

class ProductGroup(models.Model):
    CONSOLIDATION_STATUS = [('yes','Yes'),
                            ('no','No')]
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    group_id = models.IntegerField(unique=True, null=True, blank=True)
    group_name = models.CharField(unique=True, max_length=30, null=True, blank=True)
    print_name = models.CharField(max_length=30, null=True, blank=True)
    sh_name = models.CharField(max_length=30, null=True, blank=True)
    code_name = models.CharField(max_length=30, null=True, blank=True)
    consolidation_status = models.CharField(choices=CONSOLIDATION_STATUS,max_length=30, null=True, blank=True)
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


class ManufacturerManager(models.Manager):
    def get_or_create_general_manufacturer(self):
        manufacturer, created = self.get_or_create(
            name__icontains='General Manufacturer',
            defaults={'name': 'General Manufacturer'}
        )
        return manufacturer


class Manufacturer(models.Model):
    TYPE_CHOICES = [
        ('manufacturer', 'Manufacturer'),
        ('supplier', 'Supplier'),
    ]

    NARRATION = [('cash_paid_to','Cash Paid To'),
             ('cash_received_from','Cash Received From'),
             ('salary_for_the_month','Salary For The Month'),
             ('sale_of_floppy_disks','Sale of Floppy Disks'),
             ('sale_of_keyboards','Sale of Keyboards'),
             ('tour_bills_paid_to','Tour Bills Paid To'),
             ('transfer_from_bank','Transfer From Bank')]

    PURCHASE_TYPE = [('within_state','Within State'),
                     ('outside_state','Outside State'),
                     ('sale_in_transit','Sale in Transit'),
                     ('import','Import')]

    GTAX_TYPE = [('gst_registered','GST Registered'),
                 ('composite_dealer','Composite Dealer'),
                 ('unregistered_dealer','Unregistered Dealer')]


    STANDARD_FORM = [('form_c','Form C'),
                     ('form_d','Form D'),
                     ('form_37','Form 37')]

    FORM_IR = [('issue','Issue'),
               ('receive','Receive')]

    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    name = models.CharField(max_length=255, null=True, blank=True, unique=True)
    print_name = models.CharField(max_length=255, null=True, blank=True)
    sh_name = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(choices=TYPE_CHOICES, max_length=20, default='manufacturer',verbose_name='Type')
    location = models.OneToOneField(Location,on_delete=models.PROTECT,related_name='manufacturer_location',null=True,blank=True)
    gstin = models.CharField(max_length=15, validators=[validate_gstin],null=True,blank=True)
    hsn = models.CharField(max_length=15,null=True,blank=True)
    email = models.EmailField(null=True, blank=True)
    contact1 = models.CharField(max_length=20, null=True, blank=True)
    last_accessed = models.DateTimeField(default=now, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    id_no = models.CharField(max_length=30,null=True,blank=True)
    purchase_type = models.CharField(choices=PURCHASE_TYPE, max_length=30,null=True,blank=True)
    tin = models.CharField(max_length=15,null=True,blank=True)
    gtax_type = models.CharField(choices=GTAX_TYPE, max_length=30,default='gst_registered',null=True,blank=True)
    class_name = models.CharField(max_length=20, null=True, blank=True)
    contact2 = models.CharField(max_length=15, null=True, blank=True)
    telephone = models.CharField(max_length=15, null=True, blank=True)
    mobile_number = models.CharField(max_length=15, null=True, blank=True, verbose_name='Mb No')
    area = models.CharField(max_length=15, null=True, blank=True, verbose_name='Area')
    fax = models.CharField(max_length=20, null=True, blank=True)
    std_form = models.CharField(choices=STANDARD_FORM, max_length=50, null=True, blank=True)
    formIR = models.CharField(choices=FORM_IR, max_length=50, null=True, blank=True)
    customer_representative = models.CharField(max_length=15, null=True, blank=True)
    cst = models.CharField(max_length=15, null=True, blank=True,verbose_name='CST')
    purchase_account = models.CharField(max_length=50, null=True, blank=True)
    invoice_prefix = models.CharField(max_length=5, null=True, blank=True)
    margin_percentage = models.PositiveSmallIntegerField(null=True, blank=True)


    objects = ManufacturerManager()

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

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        if self.location:
            self.location.delete()



class Product(models.Model):
    STOCK_OPTION_CHOICE = [
        ('quantity_wise', 'Quantity Wise'),
        ('batch_wise', 'Batch Wise')
    ]

    TAX_CHOICE = [
        ('excluded', 'Excluded'),
        ('included', 'Included')
    ]

    UOM = [('centimeter', 'Centimeter'), ('gallon', 'Gallon'), ('liter', 'Liter'),
           ('meter', 'Meter'), ('metric_ton', 'Metric Ton'), ('milligram', 'Milligram'),
           ('pound', 'Pound')]

    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    product_name = models.CharField(max_length=255, null=True, blank=True, unique=True)
    sh_name = models.CharField(max_length=255, null=True, blank=True, unique=True)
    map_code = models.CharField(max_length=15, null=True, blank=True)
    bin_loc = models.CharField(max_length=15, null=True, blank=True)
    product_spec = models.CharField(max_length=50, null=True, blank=True)
    print_name = models.CharField(max_length=255, null=True, blank=True)
    contact = models.CharField(max_length=20, null=True, blank=True)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, related_name='product_manufacturer')
    buy_rate = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    sell_rate = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    mrp = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    net_quantity = models.PositiveIntegerField(null=True, blank=True)
    stock_option = models.CharField(choices=STOCK_OPTION_CHOICE, max_length=20, default='quantity_wise')
    group = models.ForeignKey(ProductGroup, on_delete=models.PROTECT, related_name='product_group', null=True,
                              blank=True)
    last_accessed = models.DateTimeField(default=now, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    unit_of_measurement = models.CharField(choices=UOM, max_length=30, null=True,blank=True)
    selling_discount = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    hsn = models.CharField(max_length=15, null=True, blank=True)
    sgst = models.CharField(max_length=15, null=True, blank=True)
    igst = models.CharField(max_length=15, null=True, blank=True)
    purchase_taxes_charges = models.CharField(max_length=15, null=True, blank=True) #comes under taxations
    taxes_buying_rate = models.CharField(choices=TAX_CHOICE,max_length=15, null=True, blank=True) #comes under taxations
    taxes_selling_rate = models.CharField(choices=TAX_CHOICE,max_length=15, null=True, blank=True) #comes under taxations


    def __str__(self):
        return f"{self.product_name} ({self.product_code})"

    class Meta:
        ordering = ['-id']
        db_table = 'Product'

    def save(self, *args, **kwargs):
        self.last_accessed = now()
        super().save(*args, **kwargs)


class Customer(models.Model):

    SALE_TYPE = [('cash','Cash'),
                 ('credit','Credit'),
                 ('cheque','Cheque'),
                 ('sign_bill','Sign Bill'),
                 ('bank','Bank'),
                 ('direct','Direct'),
                 ('adv_payment','Adv.Pymt')]

    NARRATION = [('cash_paid_to', 'Cash Paid To'),
             ('cash_received_from', 'Cash Received From'),
             ('salary_for_the_month', 'Salary For The Month'),
             ('sale_of_floppy_disks', 'Sale of Floppy Disks'),
             ('sale_of_keyboards', 'Sale of Keyboards'),
             ('tour_bills_paid_to', 'Tour Bills Paid To'),
             ('transfer_from_bank', 'Transfer From Bank')]

    BILLING_STAT = [('active','Active'),
                    ('on_approval','On Approval'),
                    ('suspended','Suspended')]
    SALE_STATE_LIST = [('within_state', 'Within State'),
                       ('outside_state', 'Outside State'),
                       ('sale_nil_gst', 'Sale(NIL GST)')]


    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    location = models.OneToOneField(Location,on_delete=models.PROTECT,related_name='customer_location',null=True,blank=True)
    customer_name = models.CharField(unique=True, max_length=30, null=True, blank=True)
    print_name = models.CharField(max_length=30, null=True, blank=True)
    sh_name = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    last_accessed = models.DateTimeField(default=now, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    sale_type = models.CharField(choices=SALE_TYPE,max_length=50, null=True, blank=True)
    id_no = models.CharField(max_length=30,null=True,blank=True)
    gstin = models.CharField(max_length=15, validators=[validate_gstin],null=True,blank=True,verbose_name='GSTIN')
    license1 = models.CharField(max_length=15, null=True,blank=True)
    license2 = models.CharField(max_length=15, null=True,blank=True)
    billing_stat = models.CharField(choices=BILLING_STAT,max_length=15, null=True,blank=True)
    telephone = models.CharField(max_length=15, null=True, blank=True)
    mobile_number = models.CharField(max_length=15, null=True, blank=True,verbose_name='Mb No')
    area = models.CharField(max_length=15, null=True, blank=True,verbose_name='Area') #not a charfield, change later
    customer_representative = models.CharField(max_length=15, null=True, blank=True) #not a charfield, change later
    tin = models.CharField(max_length=15, null=True, blank=True)
    cst = models.CharField(max_length=15, null=True, blank=True)
    carrier = models.CharField(max_length=15, null=True, blank=True)
    contact1 = models.CharField(max_length=15, null=True, blank=True)
    contact2 = models.CharField(max_length=15, null=True, blank=True)
    fax = models.CharField(max_length=20, null=True, blank=True)
    price_option = models.CharField(max_length=20, null=True, blank=True)
    price_table = models.CharField(max_length=20, null=True, blank=True)
    class_name = models.CharField(max_length=20, null=True, blank=True)

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

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        if self.location:
            self.location.delete()

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

#store receipt product in the form of json in receipts
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


class TaxStructure(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    TAX_TYPE = [('sales_taxes','Sales Taxes'),
                ('purchase_taxes','Purchase Taxes')]

    tax_type = models.CharField(max_length=25,choices=TAX_TYPE,null=True,blank=True)
    tax_id = models.CharField(max_length=20, blank=True,null=True, unique=True)
    sgst = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    cgst = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    igst = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    description = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f'{self.tax_type}-{self.tax_id}'

class TaxDetail(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    tax_id = models.CharField(max_length=20, blank=True)
    sgst = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    cgst = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    igst = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    description = models.CharField(max_length=50, null=True, blank=True)


    def __str__(self):
        return f"{self.tax_id}"