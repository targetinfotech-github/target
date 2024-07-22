from datetime import datetime

from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django import forms
import re
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from icecream import ic

from .models import Manufacturer, Product, ProductGroup, Customer, CustomUser
from django import forms
from .models import Receipt, ReceiptProduct, Manufacturer, Product
from django.db import transaction


def get_state_code():
    STATE_CODES = {
        "01": "Jammu and Kashmir",
        "02": "Himachal Pradesh",
        "03": "Punjab",
        "04": "Chandigarh",
        "05": "Uttarakhand",
        "06": "Haryana",
        "07": "Delhi",
        "08": "Rajasthan",
        "09": "Uttar Pradesh",
        "10": "Bihar",
        "11": "Sikkim",
        "12": "Arunachal Pradesh",
        "13": "Nagaland",
        "14": "Manipur",
        "15": "Mizoram",
        "16": "Tripura",
        "17": "Meghalaya",
        "18": "Assam",
        "19": "West Bengal",
        "20": "Jharkhand",
        "21": "Odisha",
        "22": "Chhattisgarh",
        "23": "Madhya Pradesh",
        "24": "Gujarat",
        "25": "Daman and Diu",
        "26": "Dadra and Nagar Haveli",
        "27": "Maharashtra",
        "28": "Andhra Pradesh (Old)",
        "29": "Karnataka",
        "30": "Goa",
        "31": "Lakshadweep",
        "32": "Kerala",
        "33": "Tamil Nadu",
        "34": "Puducherry",
        "35": "Andaman and Nicobar Islands",
        "36": "Telangana",
        "37": "Andhra Pradesh (New)",
        "38": "Ladakh",
        "97": "Other Territory"
    }
    return STATE_CODES

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        ))
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password check",
                "class": "form-control"
            }
        ))

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')


class ManufacturerForm(forms.ModelForm):


    PURCHASE_TYPE = [('within_state','Within State'),
                     ('outside_state','Outside State'),
                     ('sale_in_transit','Sale in Transit'),
                     ('import','Import')]
    customer_representative = forms.CharField(
        label='Rep',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter REP'
        })
    )
    telephone = forms.CharField(
        label='Tel',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telephone Number'})
    )

    name = forms.CharField(label='Name', widget=(
        forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the name', 'id': 'name_form'})))
    postal_code = forms.IntegerField(validators=[MinValueValidator(1)], widget=(
        forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code', 'id': 'postal_code_form'})))

    class_name = forms.CharField(label='Class',widget=(forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Class Name'})))

    purchase_type = forms.ChoiceField(
        choices=PURCHASE_TYPE,
        label='Purc Type',
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'purchase_type_form'})
    )
    purchase_account = forms.CharField(label='Purc Acc',widget=(forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Purchase Account'})))
    class Meta:
        model = Manufacturer
        fields = '__all__'
        widgets = {
            'print_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter the print name', 'id': 'print_name_form'}),
            'sh_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the short name'}),
            'address': forms.Textarea(
                attrs={'class': 'form-control custom-address', 'placeholder': 'Enter the address', 'rows': 4,
                       'id': 'address-form'}),
            'email': forms.EmailInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter the email', 'id': 'email-form'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the City'}),
            'state_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the State Name'}),
            'state_code': forms.TextInput(
                attrs={'class': 'form-control', 'id': 'state-code-form'}),
            'gstin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the GSTIN'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),
            'contact1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact 1'}),
            'contact2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact 2'}),
            'area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Area'}),
            'tin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter TIN'}),
            'cst': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter CST'}),
            'fax': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter FAX'}),
            'class_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Class Name'}),
            'sale_state': forms.Select(attrs={'class': 'form-control', 'id': 'sale_state_form'}),
            'formIR': forms.Select(attrs={'class': 'form-control', 'id': 'form_ir'}),
            'std_form': forms.Select(attrs={'class': 'form-control', 'id': 'std_form'}),
            'type': forms.Select(attrs={'class': 'form-control', 'id': 'std_form'}),
            'gtax_type': forms.Select(attrs={'class': 'form-control', 'id': 'gtax_type'}),
            'id_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter ID NO'}),
            'invoice_prefix': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Invoice Prefix'}),
            'hsn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter HSN'}),
            'margin_percentage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter margin%'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['sh_name'].required = True

    STATE_CODES = get_state_code()
    STATE_NAMES = {v.lower(): k for k, v in STATE_CODES.items()}

    def clean(self):
        cleaned_data = super().clean()
        state_name = self.cleaned_data['state_name'].lower()
        state_code = self.cleaned_data['state_code'].lower()
        if state_name and state_name not in self.STATE_NAMES:
            self.add_error('state_name', f'state name: {state_name} does not exists')
        if state_code and state_code not in self.STATE_CODES:
            self.add_error('state_code', f'State Code: {state_code} does not exists')
        if self.STATE_CODES['state_code'] != state_name:
            self.add_error('state_name', 'State name does not match the state code.')
            self.add_error('state_code', 'State code does not match the state name.')
        return cleaned_data


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['manufacturer', 'product_name', 'product_code', 'print_name', 'contact',
                  'buy_rate', 'sell_rate', 'mrp', 'stock_option', 'group', 'product_spec', 'map_code',
                  'selling_discount', 'hsn', 'unit_of_measurement','purchase_taxes_charges','taxes_buying_rate',
                  'taxes_selling_rate','bin_loc','sgst','igst']

    widgets = {
        'manufacturer': forms.Select(attrs={'class': 'form-control'}),
    }    # #
    # widgets = {
    #     'manufacturer': forms.Select(attrs={'class': 'form-select'}),
    #     'product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the product name'}),
    #     'product_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the product code'}),
    #     'print_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the print name'}),
    #     'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the contact number'}),
    #     'buy_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the buy rate'}),
    #     'sell_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the sell rate'}),
    #     'mrp': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the MRP'}),
    #     'stock_option': forms.Select(attrs={'class': 'form-control'}),
    #     'group': forms.Select(attrs={'class': 'form-control'}),
    # }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product_name'].required = True
        self.fields['product_code'].required = True
        self.fields['buy_rate'].required = True
        self.fields['sell_rate'].required = True
        self.fields['mrp'].required = True



class CustomerForm(forms.ModelForm):
    customer_representative = forms.CharField(
        label='Rep',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter REP'
        })
    )
    telephone = forms.CharField(
        label='Tel',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telephone Number'})
    )


    price_option = forms.CharField(label='PO',widget=(forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Price Option'})))
    customer_name = forms.CharField(label='Name' ,widget=(forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the name','id':'name_form'})))
    postal_code = forms.IntegerField(validators=[MinValueValidator(1)],widget=(forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code','id':'postal_code_form'})))
    class Meta:
        model = Customer
        # fields = ['type','name', 'print_name', 'sh_name', 'contact','hsn_code','address','email']
        # fields = ['customer_name', 'print_name', 'sh_name', 'address', 'email', 'contact', 'city', 'postal_code',
        #           'state_name', 'sale_state', 'sale_type', 'id_no', 'gstin', 'license1', 'license2', 'billing_stat',
        #           'telephone','state_code','mobile_number', 'area', 'customer_representative', 'tin', 'cst', 'carrier',
        #           'contact1','contact2','fax','price_option','']
        fields = '__all__'
        widgets = {
            'print_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the print name','id':'print_name_form'}),
            'sh_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the short name'}),
            'address': forms.Textarea(
                attrs={'class': 'form-control custom-address', 'placeholder': 'Enter the address', 'rows': 4,'id':'address-form'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter the email', 'id':'email-form'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the City'}),
            'state_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the State Name'}),
            'state_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '01-97', 'id':'state-code-form'}),
            'gstin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the GSTIN'}),
            'license1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter License1'}),
            'license2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter License2'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),
            'contact1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact 1'}),
            'contact2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact 2'}),
            'area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Area'}),
            'tin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter TIN'}),
            'cst': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter CST'}),
            'fax': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter FAX'}),
            'carrier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Carrier'}),
            'price_table': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0-9','id':'price_table_id'}),
            'class_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Class Name'}),
            'sale_state': forms.Select(attrs={'class': 'form-control','id':'sale_state_form'}),
            'sale_type': forms.Select(attrs={'class': 'form-control'}),
            'id_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter ID NO'}),
            'billing_stat': forms.Select(attrs={'class': 'form-control','id':'billing_stat_form'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer_name'].required = True
        self.fields['sh_name'].required = True
    STATE_CODES = get_state_code()


    STATE_NAMES = {v.lower(): k for k, v in STATE_CODES.items()}

    def clean(self):
        cleaned_data = super().clean()
        state_name,state_code=None,None
        if self.cleaned_data['state_name']:
            state_name = self.cleaned_data['state_name'].lower()
            if state_name not in self.STATE_NAMES:
                self.add_error('state_name', f'state name: {state_name} does not exists')
        if self.cleaned_data['state_code']:
            state_code = self.cleaned_data['state_code'].lower()
            if state_code not in self.STATE_CODES:
                self.add_error('state_code',f'State Code: {state_code} does not exists')
        if state_name and state_code:
            if self.STATE_CODES[state_code] != state_name:

                self.add_error('state_name', 'State name does not match the state code.')
                self.add_error('state_code', 'State code does not match the state name.')
        return cleaned_data


class GroupForm(forms.ModelForm):
    class Meta:
        model = ProductGroup
        # fields = ['type','name', 'print_name', 'sh_name', 'contact','hsn_code','address','email']
        fields = '__all__'
        widgets = {
            'group_id': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Group ID'}),
            'group_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Group Name'}),
            'print_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Print Name'}),
            'sh_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Sh Name'}),
            'code_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Code Name'}),
            'consolidation_code': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter the Consolidation Code'}),
            'hsn_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the HSN Code'}),
            'gcr_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the GCR Code'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group_name'].required = True


# class CustomReceiptForm(forms.Form):
#     receipt_type = [('purchases', 'Purchases'),
#                     ('adjustments', 'Adjustments'),
#                     ('opening_stock', 'Opening Stock')]
#
#     receipt_status = [('received', 'Received'),
#                       ('transit', 'Transit'),
#                       ('approved', 'Approved'),
#                       ('suspense', 'Suspense')]
#     receipt_type = forms.ChoiceField(choices=receipt_type, initial='purchases',label='receipt type')
#     receipt_status = forms.ChoiceField(choices=receipt_status, initial='received')
#     date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), initial=datetime.today())
#     manufacturer = forms.ModelChoiceField(queryset=Manufacturer.objects.all())
#     # product_name = forms.ModelChoiceField(queryset=)
#     quantity = forms.IntegerField(initial=1)
#     discount = forms.FloatField(initial=0.0)
#
#     def clean(self):
#         cleaned_data = super().clean()
#         manufacturer = cleaned_data.get('manufacturer')
#         product_name = cleaned_data.get('product_name')
#
#         if manufacturer and product_name:
#             try:
#                 product = Product.objects.get(manufacturer=manufacturer, product_name=product_name)
#             except Product.DoesNotExist:
#                 raise forms.ValidationError("Invalid product name for selected manufacturer.")
#
#         return cleaned_data
#
#     def save(self,commit=True):
#         manufacturer = self.cleaned_data['manufacturer']
#         product_name = self.cleaned_data['product_name']
#         product = Product.objects.get(manufacturer=manufacturer, product_name=product_name)
#
#         receipt_data = {
#             'receipt_type': self.cleaned_data['receipt_type'],
#             'receipt_status': self.cleaned_data['receipt_status'],
#             'date': self.cleaned_data['date'],
#             'manufacturer': manufacturer,
#             'net_amount': self.cleaned_data['net_amount'],
#         }
#
#         if commit:
#             with transaction.atomic():
#                 receipt = Receipt.objects.create(**receipt_data)
#
#                 receipt_product_data = {
#                     'receipt': receipt,
#                     'product': product,
#                     'quantity': self.cleaned_data['quantity'],
#                     'discount': self.cleaned_data['discount'],
#                 }
#                 ReceiptProduct.objects.create(**receipt_product_data)
#         else:
#             receipt = Receipt(**receipt_data)
#             receipt_product = ReceiptProduct(
#                 receipt=receipt,
#                 product=product,
#                 quantity=self.cleaned_data['quantity'],
#                 discount=self.cleaned_data['discount'],
#             )
#         return receipt, receipt_product


#
# class ReceiptForm(forms.Form):
#     receipt_type_choice = [
#         ('purchases', 'Purchases'),
#         ('adjustments', 'Adjustments'),
#         ('opening_stock', 'Opening Stock')
#     ]
#
#     receipt_status_choice = [
#         ('purchases', [
#             ('received', 'Received'),
#             ('transit', 'Transit'),
#             ('approved', 'Approved'),
#             ('suspense', 'Suspense')
#         ]),
#         ('adjustments', [
#             ('adjustment', 'Adjustment'),
#             ('transfer', 'Transfer'),
#             ('suspense', 'Suspense')
#         ]),
#         ('opening_stock', [
#             ('none', 'None')
#         ])
#     ]
#
#     receipt_type = forms.ChoiceField(choices=receipt_type_choice, label='Receipt Type')
#     receipt_status = forms.ChoiceField(choices=receipt_status_choice, label='Receipt Status')
#     date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), initial=datetime.today())
#     manufacturer = Manufacturer.objects.all()

class ReceiptForm(forms.ModelForm):
    receipt_type_choice = [
        ('purchases', 'Purchases'),
        ('adjustments', 'Adjustments'),
        ('opening_stock', 'Opening Stock')
    ]

    receipt_status_choice = [
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

    receipt_type = forms.ChoiceField(choices=receipt_type_choice, label='Receipt Type')
    receipt_status = forms.ChoiceField(choices=receipt_status_choice, label='Receipt Status')
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), initial=datetime.today())

    class Meta:
        model = Receipt
        fields = ['receipt_type', 'receipt_status', 'date', 'manufacturer']
