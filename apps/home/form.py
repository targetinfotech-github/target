from datetime import datetime

from django import forms
from .models import Manufacturer, Product, Group, Customer
from django import forms
from .models import Receipt, ReceiptProduct, Manufacturer, Product
from django.db import transaction


class ManufacturerForm(forms.ModelForm):
    class Meta:
        model = Manufacturer
        # fields = ['type','name', 'print_name', 'sh_name', 'contact','hsn_code','address','email']
        fields = ['name', 'print_name', 'sh_name', 'type', 'address', 'email', 'contact']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the name'}),
            'print_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the print name'}),
            'sh_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the short name'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter the address', 'rows': 4}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter the email'}),
            'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the contact number'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['sh_name'].required = True

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['manufacturer','product_name','product_code','print_name','contact',
                  'buy_rate','sell_rate','mrp','stock_option','group']


    # widgets = {
    #     'manufacturer': forms.Select(attrs={'class': 'form-control'}),
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
#

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        # fields = ['type','name', 'print_name', 'sh_name', 'contact','hsn_code','address','email']
        fields = ['customer_name', 'print_name', 'sh_name', 'address', 'email', 'contact']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the name'}),
            'print_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the print name'}),
            'sh_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the short name'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter the address', 'rows': 4}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter the email'}),
            'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the contact number'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer_name'].required = True
        self.fields['sh_name'].required = True



class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        # fields = ['type','name', 'print_name', 'sh_name', 'contact','hsn_code','address','email']
        fields = '__all__'
        widgets = {
            'group_id': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Group ID'}),
            'group_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Group Name'}),
            'print_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Print Name'}),
            'sh_name': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Enter the Sh Name'}),
            'code_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Code Name'}),
            'consolidation_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Consolidation Code'}),
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
    date = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}),initial=datetime.today())

    class Meta:
        model = Receipt
        fields = ['receipt_type','receipt_status','date','manufacturer']

