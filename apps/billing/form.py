from datetime import datetime

from django.core.validators import MinValueValidator
from django.db.models import Case, When, IntegerField, Q
from django.forms import formset_factory
from django.utils.translation import gettext_lazy as _
from django import forms
import re
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from icecream import ic

from .models import Manufacturer, Product, ProductGroup, Customer, CustomUser, Location, TaxStructure, SalesRep, Area, \
    ManufacturerArea, ManufacturerRep, Carriers, Units, Departments, Division, DiscountClass, CustomerClass, \
    BankDetails, PaymentDetails
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


class LocationForm(forms.ModelForm):
    postal_code = forms.IntegerField(validators=[MinValueValidator(1)], required=False, widget=(
        forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code', 'id': 'postal_code_form'})))

    class Meta:
        model = Location
        fields = ['address', 'city', 'postal_code', 'state_name', 'sale_state', 'state_code']
        widgets = {
            'address': forms.Textarea(
                attrs={'class': 'form-control custom-address', 'placeholder': 'Enter the address',
                       'id': 'address-form'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the City'}),
            'state_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the State Name'}),
            'sale_state': forms.Select(attrs={'class': 'form-control', 'id': 'sale_state_form'}),
            'state_code': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': '01-97', 'id': 'state-code-form'}),
        }

    STATE_CODES = get_state_code()
    STATE_NAMES = {v.lower(): k for k, v in STATE_CODES.items()}

    def clean(self):
        cleaned_data = super().clean()
        state_name, state_code = None, None
        if self.cleaned_data['state_name']:
            state_name = self.cleaned_data['state_name'].lower()
            if state_name not in self.STATE_NAMES:
                self.add_error('state_name', f'state name: {state_name} does not exists.')
        if self.cleaned_data['state_code']:
            state_code = self.cleaned_data['state_code'].lower()
            if state_code not in self.STATE_CODES:
                self.add_error('state_code', f'State Code: {state_code} does not exists')
        if state_name and state_code:
            if self.STATE_CODES[state_code].lower() != state_name.lower():
                self.add_error('state_name', f'State name does not match the state code.')
                self.add_error('state_code', 'State code does not match the state name.')
        return cleaned_data

    def save(self, commit=True):
        state_name = None
        state_code = None
        if self.cleaned_data['state_name']:
            state_name = self.cleaned_data['state_name'].lower()
        if self.cleaned_data['state_code']:
            state_code = self.cleaned_data['state_code'].lower()
        if state_name and not state_code:
            for key, value in self.STATE_CODES.items():
                if value.lower() == state_name:
                    state_code = key
        elif state_code and not state_name:
            state_name = self.STATE_CODES[state_code]
        instance = super().save(commit=False)
        instance.state_name = state_name
        instance.state_code = state_code
        if commit:
            print(f'commit: {commit}')
            instance.save()
        return instance


class ManufacturerForm(forms.ModelForm):

    PURCHASE_TYPE = [('within_state', 'Within State'),
                     ('outside_state', 'Outside State'),
                     ('sale_in_transit', 'Sale in Transit'),
                     ('import', 'Import')]

    sales_representative = forms.ModelChoiceField(
        SalesRep.objects.exclude(name='AUTO'),
        label='Rep', required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    telephone = forms.CharField(
        label='Tel', required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telephone Number'})
    )

    name = forms.CharField(label='Name', widget=(
        forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the name', 'id': 'name_form'})))

    customer_class = forms.ModelChoiceField(
        queryset=CustomerClass.objects.all(),
        label='Class', required=False,
                                 widget=(forms.Select(attrs={'class': 'form-control'})))

    purchase_type = forms.ChoiceField(
        choices=PURCHASE_TYPE,
        label='Purc Type', required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'purchase_type_form'})
    )
    purchase_account = forms.CharField(label='Purc Acc', required=False, widget=(
        forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Purchase Account'})))

    area = forms.ModelChoiceField(
        Area.objects.exclude(name='AUTO'),
        label='Area', required=False,
        widget=(forms.Select(attrs={'class': 'form-control'}))
    )
    class Meta:
        model = Manufacturer
        fields = '__all__'
        widgets = {
            'print_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter the print name', 'id': 'print_name_form'}),
            'sh_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the short name'}),
            'email': forms.EmailInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter the email', 'id': 'email-form'}),
            'gstin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the GSTIN'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),
            'contact1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact 1'}),
            'contact2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact 2'}),
            'tin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter TIN'}),
            'cst': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter CST'}),
            'fax': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter FAX'}),
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


class ProductForm(forms.ModelForm):
    UOM = [('','---------'),('centimeter', 'Centimeter'), ('gallon', 'Gallon'), ('liter', 'Liter'),
           ('meter', 'Meter'), ('metric_ton', 'Metric Ton'), ('milligram', 'Milligram'),
           ('pound', 'Pound')]
    unit_of_measurement = forms.CharField(label='UOM',
                                          widget=forms.Select(choices=UOM,attrs={'class': 'form-control'}),required=False)

    class Meta:
        model = Product

        fields = '__all__'
        widgets = {
            'manufacturer': forms.Select(attrs={'class': 'form-control'}),
            'group': forms.Select(attrs={'class': 'form-control'}),
            'product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the product name'}),
            'sh_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Sh Name'}),
            'map_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Map Code'}),
            'bin_loc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Bin Loc'}),
            'product_spec': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Product Spec'}),
            'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the contact number'}),
            'print_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Print Name'}),
            'hsn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the HSN'}),
            'sgst': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SGST', 'id': 'gst_tax_form'}),
            'igst': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IGST', 'id': 'gst_tax_form'}),
            'purchase_taxes_charges': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Purchase Taxes Charges'}),
            'taxes_buying_rate': forms.Select(attrs={'class': 'form-control', 'id': 'taxes_rate_form'}),
            'taxes_selling_rate': forms.Select(attrs={'class': 'form-control', 'id': 'taxes_rate_form'}),
            'buy_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '+int', 'id': 'price_rate'}),
            'sell_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '+int', 'id': 'price_rate'}),
            'mrp': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '+int', 'id': 'price_rate'}),
            'net_quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Net Quantity'}),
            'selling_discount': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': '+int%', 'id': 'discount_form'}),
            'stock_option': forms.Select(attrs={'class': 'form-control', 'id': 'stock_option_forms'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product_name'].required = True
        self.fields['buy_rate'].required = True
        self.fields['sell_rate'].required = True
        self.fields['mrp'].required = True


class CustomerForm(forms.ModelForm):
    telephone = forms.CharField(
        label='Tel', required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telephone Number'})
    )

    price_option = forms.CharField(label='PO', required=False, widget=(
        forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Price Option'})))
    customer_name = forms.CharField(label='Name', widget=(
        forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the name', 'id': 'name_form'})))

    area_object = Area.objects.get_or_create_model()
    area = forms.ModelChoiceField(
        Area.objects.annotate(
            order_priority=Case(
                When(name='AUTO', then=0),
                default=1,
                output_field=IntegerField()
            )
        ).order_by('order_priority', 'name'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial=area_object
    )
    sales_object = SalesRep.objects.get_or_create_model()
    sales_representative = forms.ModelChoiceField(
        SalesRep.objects.annotate(
            order_priority=Case(
                When(name='AUTO', then=0),
                default=1,
                output_field=IntegerField()
            )
        ).order_by('order_priority', 'name'),
        required=False,
        label='Rep',
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial=sales_object
    )
    class Meta:
        model = Customer
        # fields = ['type','name', 'print_name', 'sh_name', 'contact','hsn_code','address','email']
        # fields = ['customer_name', 'print_name', 'sh_name', 'address', 'email', 'contact', 'city', 'postal_code',
        #           'state_name', 'sale_state', 'sale_type', 'id_no', 'gstin', 'license1', 'license2', 'billing_stat',
        #           'telephone','state_code','mobile_number', 'area', 'customer_representative', 'tin', 'cst', 'carrier',
        #           'contact1','contact2','fax','price_option','']
        fields = '__all__'
        widgets = {
            'print_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter the print name', 'id': 'print_name_form'}),
            'sh_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the short name'}),
            'email': forms.EmailInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter the email', 'id': 'email-form'}),
            'gstin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the GSTIN'}),
            'license1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter License1'}),
            'license2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter License2'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),
            'contact1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact 1'}),
            'contact2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact 2'}),
            'tin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter TIN'}),
            'cst': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter CST'}),
            'fax': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter FAX'}),
            'carrier': forms.Select(attrs={'class': 'form-control'}),
            'price_table': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': '0-9', 'id': 'price_table_id'}),
            'class_name': forms.Select(attrs={'class': 'form-control'}),
            'sale_type': forms.Select(attrs={'class': 'form-control'}),
            'id_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter ID NO'}),
            'billing_stat': forms.Select(attrs={'class': 'form-control', 'id': 'billing_stat_form'}),
        }

    def __init__(self, *args, **kwargs):
        # initial = kwargs.get('initial', {})
        # if initial:
        #     initial['area'] = initial['area']  # Ensure instance data is overridden
        #     initial['sales_representative'] = initial['sales_representative']
        # kwargs['initial'] = initial
        super().__init__(*args, **kwargs)
        self.fields['customer_name'].required = True
        self.fields['sh_name'].required = True


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
            'consolidation_status': forms.Select(attrs={'class': 'form-control', 'id': 'consolidation_status_form'}),
            'hsn_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the HSN Code'}),
            'gcr_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the GCR Code'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group_name'].required = True


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


class TaxStructureForm(forms.ModelForm):
    tax_id = description = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control','readonly':'readonly'}))
    sgst = forms.FloatField(label='SGST',
                            widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'SGST %','id': 'tax_form'}))
    cgst = forms.FloatField(label='CGST',
                            widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'CGST %','id': 'tax_form'}))
    igst = forms.FloatField(label='IGST',
                            widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'IGST %','id': 'tax_form'}))
    description = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter Description', 'id': 'description_form'}))
    class Meta:
        model = TaxStructure
        fields = ['sgst','cgst','igst','description']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'igst' in self.fields:
            self.fields['igst'].required = False
        if 'cgst' in self.fields:
            self.fields['cgst'].required = False
        if 'sgst' in self.fields:
            self.fields['sgst'].required = False
        if 'description' in self.fields:
            self.fields['description'].required = False

TaxStructureFormSet = formset_factory(TaxStructureForm,extra=0)

class SalesRepForm(forms.ModelForm):
    class Meta:
        model = SalesRep
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter the Name', 'id': 'name_form'}),
            'sh_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the short name'}),
            'rep_type_id': forms.Select(attrs={'class': 'form-control'}),
            'rep_indent': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Rep Indent'}),
            'address': forms.Textarea(
                attrs={'class': 'form-control custom-address', 'placeholder': 'Enter the address',
                       'id': 'address-form'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telephone'}),
            'fax': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter FAX'}),
            'state_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter State Name'}),
            # 'company': forms.Select(attrs={'class': 'form-control', 'id': 'company'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter City'}),
            'postal_code': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter PIN'}),
        }


class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter the Name', 'id': 'name_form'}),
            'sh_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the short name'}),
            'area_status': forms.Select(attrs={'class': 'form-control'}),
            'pin_code': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Pin Code'}),
        }

class CustomerDisplayForm(forms.Form):
    customer = forms.ChoiceField(label='Customer',widget=forms.Select(choices=[],attrs={'class': 'form-control','id':'name_form'}))
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        customer_data = Customer.objects.filter(is_auto_area=True).distinct().values_list('id', 'customer_name')
        self.fields['customer'].choices = [(id, name) for id, name in customer_data]


class ManufacturerAreaForm(forms.Form):
    manufacturer = forms.ChoiceField(label='Manufacturer',widget=forms.Select(choices=[],attrs={'class': 'form-control','id':'name_form'}))
    area = forms.ChoiceField(label='Area',widget=forms.Select(choices=[],attrs={'class': 'form-control','id':'name_form'}))

    class Meta:
        fields = ['manufacturer','area']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial = kwargs.pop('initial')
        if initial['manufacturer']:
            manufacturer = Manufacturer.objects.filter(id=initial['manufacturer']).values_list('id','name')
            self.fields['manufacturer'].choices = [(id, name) for id, name in manufacturer]
            manufacturer_area = ManufacturerArea.objects.get(id=initial['id'])
            if manufacturer_area.area is not None:
                area_list =Area.objects.exclude(Q(id=manufacturer_area.area.id) | Q(name='AUTO')).values_list('id','name')
                self.fields['area'].choices = [(manufacturer_area.area.id,manufacturer_area.area.name),(None,'-------')] + [(id, name) for id, name in area_list]
            else:
                area_list = Area.objects.all().values_list('id','name').exclude(name='AUTO')
                self.fields['area'].choices =[(None,'-------')] + [(id,name) for id, name in area_list]


ManufacturerAreaFormset = formset_factory(ManufacturerAreaForm, extra=0)


class ManufacturerRepForm(forms.Form):
    manufacturer = forms.ChoiceField(widget=forms.Select(choices=[],attrs={'class': 'form-control','id':'name_form'}))
    sales_rep = forms.ChoiceField(widget=forms.Select(choices=[],attrs={'class': 'form-control','id':'name_form'}))

    class Meta:
        fields = ['manufacturer','sales_rep']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial = kwargs.pop('initial')
        if initial['manufacturer']:
            manufacturer = Manufacturer.objects.filter(id=initial['manufacturer']).values_list('id','name')
            self.fields['manufacturer'].choices = [(id, name) for id, name in manufacturer]
            manufacturer_rep = ManufacturerRep.objects.get(id=initial['id'])
            if manufacturer_rep.sales_rep is not None:
                rep_list =SalesRep.objects.exclude(Q(id=manufacturer_rep.sales_rep.id) | Q(name='AUTO')).values_list('id','name')
                self.fields['sales_rep'].choices = [(manufacturer_rep.sales_rep.id,manufacturer_rep.sales_rep.name),(None,'-------')] + [(id, name) for id, name in rep_list]
            else:
                rep_list = SalesRep.objects.all().values_list('id','name').exclude(name='AUTO')
                self.fields['sales_rep'].choices =[(None,'-------')] + [(id,name) for id, name in rep_list]


ManufacturerRepFormset = formset_factory(ManufacturerRepForm, extra=0)



class CarrierForm(forms.ModelForm):
    postal_code = forms.IntegerField(label='PIN', required=False, widget=(
        forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter PIN'})))
    class Meta:
        model = Carriers
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter the Name', 'id': 'name_form'}),
            'sh_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the short name'}),
            'address': forms.Textarea(
                attrs={'class': 'form-control custom-address', 'placeholder': 'Enter the Address',
                       'id': 'address-form'}),
            'remarks': forms.Textarea(
                attrs={'class': 'form-control custom-address', 'placeholder': 'Enter the Remarks',
                       'id': 'address-form'}),
            'gstin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the GSTIN'}),
            'e_way_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the E Way ID'}),
            'regn_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Regn NO'}),

            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telephone'}),
            'fax': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter FAX'}),
            'state_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter State Name'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter City'}),
        }


class GeneralSelectionListForm(forms.Form):
    name = forms.CharField(max_length=30,required=True,widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Name', 'id': 'name_form'}))
    sh_name = forms.CharField(max_length=10,required=True,widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Short Name', 'id':'sh_name_form'}))
    remarks = forms.CharField(max_length=255,required=False,widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Remarks', 'id':'address-form'}))
    brand_code = forms.CharField(required=False,widget=forms.TextInput(attrs={'class': 'form-control','readonly':'readonly'}))

    def __init__(self,*args,**kwargs):
        self.model = kwargs.pop('model',None)
        super().__init__(*args,**kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if self.model and self.model.objects.filter(name=cleaned_data['name']):
            raise ValidationError(f'Name {cleaned_data['name']} already exists')
        return cleaned_data


class DivisionForm(forms.ModelForm):
    class Meta:
        model = Division
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter the Name', 'id': 'name_form'}),
            'sh_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the short name'}),
            'division_id': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the short name'}),
            'customer': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Enter the short name'}),
        }

class BankDetailsForm(forms.ModelForm):
    class Meta:
        model = BankDetails
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter the Name', 'id': 'name_form'}),
        }


class PaymentDetailsForm(forms.ModelForm):
    class Meta:
        model = PaymentDetails
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter the Name', 'id': 'name_form'}),
            'type_id': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Type ID'}),
            'account_link': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Acc Link'}),
            'domination_breakup': forms.Select(attrs={'class': 'form-control'}),
            'payment_mode': forms.Select(attrs={'class': 'form-control'}),
        }


