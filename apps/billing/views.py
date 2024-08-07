# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import time

from django import template
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction, IntegrityError
from django.db.models import Count, Q, QuerySet
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.urls import reverse
from django.views.generic import FormView
from icecream import ic

from apps.billing.services.decorators import measure_execution_time
from apps.billing.form import *
from django.shortcuts import render, redirect
from apps.billing.models import Manufacturer, Product, Receipt, ReceiptProduct, ProductGroup, Customer, CustomUser, \
    Location, TaxStructure, SalesRep, Area, ManufacturerArea, Departments, Division, DiscountClass
import json

# views.py or any module

import logging

from apps.billing.services.resource_manager import SetupContext
from apps.billing.services.search_manager import SearchService, masterSearchEndpoint

# Get an instance of a logger
logger = logging.getLogger(__name__)


@measure_execution_time
@login_required(login_url="/login/")
def index(request):
    ProductGroup.objects.get_or_create_general_group()
    Manufacturer.objects.get_or_create_general_manufacturer()
    context = {'segment': 'index'}
    manufacturer = Manufacturer.objects.count()
    group = ProductGroup.objects.count()
    product = Product.objects.count()
    customer = Customer.objects.count()
    location = Location.objects.count()
    print(f'group: {group}')
    print(f'manufacturer: {manufacturer}')
    print(f'product: {product}')
    print(f'customer: {customer}')
    print(f'location: {location}')
    print(f'TaxStructure: {TaxStructure.objects.count()}')
    html_template = loader.get_template('billing/dashboard.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
@measure_execution_time
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        load_template = request.path.split('/')[-1]
        ic(load_template)
        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template
        html_template = loader.get_template('billing/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')


def pagination(request, queryset):
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj


def login_view(request):
    form = LoginForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                messages.error(request, 'Invalid credentials')
        else:
            messages.error(request, f'Invalid Form')

    return render(request, "accounts/login.html", {"form": form})


def register_user(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            email = form.cleaned_data.get('email')
            if CustomUser.objects.filter(email__iexact=email).exists():
                messages.error(request, 'Email exists')
                return redirect('login')
            try:
                user = authenticate(username=username, password=raw_password)
            except Exception as e:
                messages.error(request, f'Exception occurred: {e}. Kindly register again')
                return redirect('register')
            form.save()
            messages.success(request, f'User created - please Sign IN.')

        else:
            messages.error(request, f'Invalid Form')
            # return redirect('register')
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required(login_url='login')
def Logout(request):
    logout(request)
    messages.success(request, '✅ Successfully Logged Out!')
    return redirect(reverse('login'))


def delete_models(request, model, name=None):
    try:
        model.delete()
        messages.success(request, f'{name} is deleted successfully')
    except Exception as e:
        if model:
            messages.error(request, f'Exception occurred: {e}. {name} not Deleted')


def create_manufacturer(request):
    try:
        if request.method == 'POST':
            manufacturer_form = ManufacturerForm(request.POST)
            location_form = LocationForm(request.POST)

            if location_form.is_valid():
                try:
                    location_instance = location_form.save()
                except Exception as e:
                    print(e)
                    location_instance = None
                    messages.error(request, 'Exception occurred while creating the location. Please submit the form again.')
            else:
                location_instance = None
            if location_instance:
                if manufacturer_form.is_valid():
                    name = manufacturer_form.cleaned_data['name']
                    try:
                        manufacturer = manufacturer_form.save(commit=False)
                        manufacturer.location = location_instance
                        manufacturer.save()
                        messages.success(request, f'Manufacturer {name} created successfully.')
                        return redirect('create_manufacturer')
                    except Exception as e:
                        if not Manufacturer.objects.filter(name=name).exists():
                            try:
                                Location.objects.get(id=location_instance.id).delete()
                            except:
                                pass
                            print(e)
                            messages.error(request,
                                           'Exception occurred while creating the manufacturer. Please submit the form again.')
                else:
                    Location.objects.get(id=location_instance.id).delete()
                    print('invalid form')
        else:
            manufacturer_form = ManufacturerForm()
            location_form = LocationForm()

        master_data = Manufacturer.objects.exists()
        if not master_data:
            try:
                Manufacturer.objects.get_or_create_general_manufacturer()
            except Exception as e:
                print(e)
                master_data = Manufacturer.objects.exists()
        context_obj = SetupContext(model_search='manufacturer', page_obj=master_data, operation='create',segment='master-manufacturer',
                                   manufacturer_form = manufacturer_form,location_form=location_form)
        context = context_obj.get_master_context()
        return render(request, 'billing/manufacturer.html', context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def get_manufacturer_modal(request):
    try:
        manufacturer_data = Manufacturer.objects.annotate(
            product_count=Count('product_manufacturer')
        ).values('id', 'name', 'type', 'sh_name', 'print_name', 'product_count').order_by('name')

        if request.method == 'POST':
            if 'submit_selected_record' in request.POST:
                id = request.POST['submit_selected_record']
                return redirect('update_manufacturer', int(id))
            elif 'delete_selected_record' in request.POST:
                id = request.POST['delete_selected_record']
                model = Manufacturer.objects.get(id=id)
                delete_models(request, model, name=model.name)
                return redirect('create_manufacturer')
            else:
                messages.info(request, 'No operation performed.')
                return redirect('create_manufacturer')
        page_obj = pagination(request, manufacturer_data)
        context_obj = SetupContext(model_search='manufacturer_modal', page_obj=page_obj, operation='modal',segment='master-product')
        context = context_obj.get_master_context()

        if not manufacturer_data:
            messages.info(request, 'Records not found')
            return render(request, 'billing/manufacturer.html', context=context)
        else:
            return render(request, 'billing/manufacturer.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request,'billing/page-404.html')
    except:
        return render(request,'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def update_manufacturer(request, pk):
    try:
        try:
            manufacturer_data = Manufacturer.objects.get(id=pk)
        except Manufacturer.DoesNotExist:
            return render(request, 'billing/page-404.html')
        location_data, created = Location.objects.get_or_create(manufacturer_location__id=pk)

        if manufacturer_data.location is None:
            manufacturer_data.location = location_data
            manufacturer_data.save()

        if request.method == 'POST':
            manufacturer_form = ManufacturerForm(request.POST, instance=manufacturer_data)
            location_form = LocationForm(request.POST, instance=location_data)

            if location_form.is_valid():
                try:
                    # Save the location form to get the Location instance
                    location_instance = location_form.save()
                except Exception as e:
                    location_instance = None
                    messages.error(request,
                                   'Exception occurred while creating the location. Please submit the form again.')
            else:
                location_instance = None
            if location_instance:
                if manufacturer_form.is_valid():
                    name = manufacturer_form.cleaned_data['name']
                    try:
                        manufacturer = manufacturer_form.save(commit=False)
                        manufacturer.location = location_instance  # Assign Location instance
                        manufacturer.save()
                        messages.success(request, f'Manufacturer {name} updated successfully.')
                        return redirect('create_manufacturer')
                    except Exception as e:
                        if not Manufacturer.objects.filter(name=name).exists():
                            try:
                                Location.objects.filter(id=location_instance.id).delete()
                            except:
                                pass
                        messages.error(request,
                                       'Exception occurred while creating the manufacturer. Please submit the form again.')
                else:
                    Location.objects.get(id=location_instance.id).delete()
                    print('invalid form')
        else:
            manufacturer_form = ManufacturerForm(instance=manufacturer_data)
            location_form = LocationForm(instance=location_data)
        context_obj = SetupContext(model_search='manufacturer', page_obj=manufacturer_data, operation='update',segment='master-product',
                                   manufacturer_form=manufacturer_form,location_form=location_form)
        context = context_obj.get_master_context()

        return render(request, 'billing/manufacturer.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def delete_manufacturer(request):
    try:
        manufacturer_data = Manufacturer.objects.annotate(
            product_count=Count('product_manufacturer')
        ).values(
            'id', 'name', 'type', 'sh_name', 'print_name', 'product_count'
        ).order_by('name')
        page_obj = pagination(request, manufacturer_data)
        context_obj = SetupContext(model_search='manufacturer_modal', page_obj=page_obj, operation='delete',segment='master-product')
        context = context_obj.get_master_context()

        if not manufacturer_data:
            messages.info(request, 'Records not found')
            return render(request, 'billing/manufacturer.html', context=context)
        else:
            return render(request, 'billing/manufacturer.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def view_manufacturer(request):
    try:
        query = ''
        if request.method == 'POST':
            manufacturer_name = request.POST.get('manufacturer_name')
            if manufacturer_name:
                manufacturer_data = Manufacturer.objects.filter(name__icontains=manufacturer_name). \
                    values('id', 'name', 'print_name', 'sh_name', 'contact1').order_by('name')
            else:
                manufacturer_data = Manufacturer.objects.all().values('id', 'name', 'print_name', 'sh_name', 'contact1') \
                    .order_by('name')
        else:
            manufacturer_data = Manufacturer.objects.all().values('id', 'name', 'print_name', 'sh_name', 'contact1') \
                .order_by('name')
        page_obj = pagination(request, manufacturer_data)
        context_obj = SetupContext(model_search='manufacturer', page_obj=page_obj, operation='view',segment='master-product')
        context = context_obj.get_master_context()

        if not manufacturer_data:
            messages.info(request, 'Records not found')
            return render(request, 'billing/manufacturer.html', context=context)
        else:
            return render(request, 'billing/manufacturer.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def create_product(request):
    try:
        ProductGroup.objects.get_or_create_general_group()
        Manufacturer.objects.get_or_create_general_manufacturer()
        if request.method == 'POST':
            form = ProductForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data['product_name']
                form.save()
                messages.success(request, f'Product {name} created')
                return redirect('create_product')
        else:
            form = ProductForm()
        product_data = Product.objects.exists()
        context_obj = SetupContext(model_search='product', page_obj=product_data, operation='create',segment='master-product',
                                   form=form)
        context = context_obj.get_master_context()

        return render(request, 'billing/products.html', context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def get_product_modal(request):
    try:
        product_data = Product.objects.select_related('manufacturer'). \
            values('id', 'product_name', 'product_spec',
                   'manufacturer__name', 'buy_rate', 'sell_rate').order_by('product_name')
        # form = ProductForm()
        if request.method == 'POST':
            if 'submit_selected_record' in request.POST:
                id = request.POST['submit_selected_record']
                return redirect('update_product', int(id))
            elif 'delete_selected_record' in request.POST:
                id = request.POST['delete_selected_record']
                model = Product.objects.get(id=id)
                delete_models(request, model, name=model.product_name)
                return redirect('create_product')
            else:
                messages.info(request, 'No operation performed.')
                return redirect('create_product')
        page_obj = pagination(request, product_data)
        context_obj = SetupContext(model_search='product_model', page_obj=page_obj, operation='modal',segment='master-product')
        context = context_obj.get_master_context()

        if not product_data:
            messages.info(request, 'Records not found')
            return render(request, 'billing/products.html', context=context)
        else:
            return render(request, 'billing/products.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def delete_product(request):
    try:
        product_data = Product.objects.select_related('manufacturer'). \
            values('id', 'product_name', 'product_spec',
                   'manufacturer__name', 'buy_rate', 'sell_rate').order_by('product_name')
        page_obj = pagination(request, product_data)
        context_obj = SetupContext(model_search='product_modal', page_obj=page_obj, operation='delete',segment='master-product')
        context = context_obj.get_master_context()
        if not product_data:
            messages.info(request, 'Records not found')
            return render(request, 'billing/products.html', context=context)
        else:
            return render(request, 'billing/products.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def update_product(request, pk):
    try:
        product_data = Product.objects.get(id=pk)
        if request.method == 'POST':
            form = ProductForm(request.POST, instance=product_data)
            if form.is_valid():
                name = form.cleaned_data['product_name']
                form.save()
                messages.success(request, f'Product {name} updated')
                return redirect('create_product')
        else:
            form = ProductForm(instance=product_data)
        context_obj = SetupContext(model_search='product', page_obj=product_data, operation='update',segment='product',
                                   form=form)
        context = context_obj.get_master_context()

        return render(request, 'billing/products.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def view_product(request):
    try:
        query = ''
        results = Product.objects.select_related('manufacturer').values(
            'id', 'product_name','product_spec', 'manufacturer__name', 'buy_rate', 'sell_rate',
            'manufacturer', 'buy_rate', 'sell_rate').order_by('product_name')
        page_obj = pagination(request, results)
        ic(page_obj)
        context_obj = SetupContext(model_search='product', page_obj=page_obj, operation='view',segment='product')
        context = context_obj.get_master_context()
        ic(context)
        if not results:
            messages.info(request, 'Records not found')
            return render(request, 'billing/products.html', context=context)
        else:
            return render(request, 'billing/products.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def get_receipt_modal(request):
    try:
        if request.method == 'POST':
            form = ReceiptForm(request.POST)
            if form.is_valid():
                receipt = form.save()
                id = receipt.id
                return redirect('add_product', pk=id)
        else:
            form = ReceiptForm()

        context = {'form': form, 'flag': 'modal', 'segment': 'receipt'}
        return render(request, 'billing/receipt.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except Exception as e:
        print(e)
        return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def create_receipt(request, pk):
    try:
        try:
            receipt = Receipt.objects.get(id=pk)
        except Receipt.DoesNotExist:
            return redirect('get_receipt_modal')
        except Exception as e:
            print('Exception occurred while obtaining receipt object: {}'.format(e))
            return redirect('billing')
        product_data = Product.objects.filter(manufacturer=receipt.manufacturer)
        if request.method == 'POST':
            reset = request.POST.get('reset', None)
            submit = request.POST.get('submit', None)
            if reset is not None:
                receipt.delete()
                return redirect('billing')
            elif submit is not None:
                product_inputs = []
                net_amount = request.POST.get('net_amount_input', '')
                for key, value in request.POST.items():
                    if key.startswith('product_name_'):
                        index = int(key.split('_')[-1])
                        product_id = value
                        quantity = int(request.POST.get(f'quantity_{index}', 0))
                        discount = float(request.POST.get(f'discount_{index}', 0.0))
                        product_inputs.append({
                            'product_id': product_id,
                            'quantity': quantity,
                            'discount': discount,
                        })

                if product_inputs:
                    with transaction.atomic():
                        for product_info in product_inputs:
                            product = Product.objects.get(id=product_info['product_id'])
                            receipt_product = ReceiptProduct.objects.create(
                                receipt=receipt,
                                product=product,
                                quantity=product_info['quantity'],
                                discount=product_info['discount'],
                            )
                    receipt.net_amount = net_amount
                    receipt.save()
                    print(
                        f'receipt_product:{receipt_product.product.product_name}, quantity:{receipt_product.quantity}, discount:{receipt_product.discount}')
                else:
                    receipt.delete()
                return redirect('billing')
        context = {'flag': 'product', 'product_data': product_data}
        return render(request, 'billing/receipt.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except Exception as e:
        print(e)
        return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def create_group(request):
    try:
        if request.method == 'POST':
            form = GroupForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data['group_name']
                form.save()
                messages.success(request, f'Group {name} created')
                return redirect('create_group')
        else:
            form = GroupForm()
        group_data = ProductGroup.objects.exists()
        if not group_data:
            try:
                ProductGroup.objects.get_or_create_general_group()
            except Exception as e:
                print(e)
            group_data = ProductGroup.objects.exists()
        context_obj = SetupContext(model_search='group', page_obj=group_data, operation='create',segment='master-selection-group',
                                   form=form)
        context = context_obj.get_master_context()
        return render(request, 'billing/group.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def view_group(request):
    try:
        if request.method == 'POST':
            group_name = request.POST.get('group_name').order_by('group_name')
            if group_name:
                group_data = ProductGroup.objects.filter(group_name=group_name).order_by('group_name')
            else:
                group_data = ProductGroup.objects.all().order_by('group_name')
        else:
            group_data = ProductGroup.objects.all().order_by('group_name')
        page_obj = pagination(request, group_data)
        context_obj = SetupContext(model_search='group', page_obj=page_obj, operation='view',segment='master-selection-group')
        context = context_obj.get_master_context()
        if not group_data:
            messages.info(request, 'Records not found')
            return render(request, 'billing/group.html', context=context)
        else:
            return render(request, 'billing/group.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def get_group_modal(request):
    try:
        group_data = ProductGroup.objects.annotate(
            product_count=Count('product_group')
        ).values('id', 'group_id', 'group_name',
                 'print_name', 'sh_name', 'hsn_code', 'product_count').order_by('group_name')

        if request.method == 'POST':
            if 'submit_selected_record' in request.POST:
                id = request.POST['submit_selected_record']
                return redirect('update_group', int(id))
            elif 'delete_selected_record' in request.POST:
                id = request.POST['delete_selected_record']
                model = ProductGroup.objects.get(id=id)
                delete_models(request, model, name=model.group_name)
                return redirect('create_group')
            else:
                messages.info(request, 'No operation performed.')
                return redirect('create_group')
        page_obj = pagination(request, group_data)
        context_obj = SetupContext(model_search='group', page_obj=page_obj, operation='modal',segment='master-selection-group')
        context = context_obj.get_master_context()
        if not group_data:
            messages.info(request, 'Records not found')
            return render(request, 'billing/group.html', context=context)
        else:
            return render(request, 'billing/group.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except Exception as e:
        print(e)
        return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def update_group(request, pk):
    try:
        group_data = ProductGroup.objects.get(id=pk)
        if request.method == 'POST':
            form = GroupForm(request.POST, instance=group_data)
            if form.is_valid():
                name = form.cleaned_data['group_name']
                form.save()
                messages.success(request, f'Group {name} updated')
                return redirect('create_group')
        else:
            form = GroupForm(instance=group_data)
        context_obj = SetupContext(model_search='group', page_obj=group_data, operation='update',segment='master-selection-group',
                                   form=form)
        context = context_obj.get_master_context()
        return render(request, 'billing/group.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def delete_group(request):
    try:
        group_data = ProductGroup.objects.annotate(
            product_count=Count('product_group')
        ).values('id', 'group_id', 'group_name',
                 'print_name', 'sh_name', 'hsn_code', 'product_count').order_by('group_name')
        page_obj = pagination(request, group_data)
        context_obj = SetupContext(model_search='group_modal', page_obj=page_obj, operation='delete',segment='master-selection-group')
        context = context_obj.get_master_context()
        if not group_data:
            messages.info(request, 'Records not found')
            return render(request, 'billing/group.html', context=context)
        else:
            return render(request, 'billing/group.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def create_customer(request):
    try:
        if request.method == 'POST':
            location_form = LocationForm(request.POST)
            customer_form = CustomerForm(request.POST)
            if location_form.is_valid():
                try:
                    location_instance = location_form.save()
                except Exception as e:
                    print(e)
                    location_instance = None
                    messages.error(request,
                                   'Exception occurred while creating the location. Please submit the form again.')
            else:
                location_instance = None
            if location_instance:
                if customer_form.is_valid():
                    ic(customer_form.fields.items())
                    name = customer_form.cleaned_data.get('customer_name','')
                    area = customer_form.cleaned_data.get('area','')
                    sales_representative = customer_form.cleaned_data.get('sales_representative','')
                    try:
                        customer = customer_form.save(commit=True)
                        customer.location = location_instance
                        if area:
                            ic(area.name)
                            if area.name == 'AUTO':
                                ic('auto area')
                                customer.is_auto_area = True
                            ic(customer.is_auto_area)
                            manufacturer_area, created = ManufacturerArea.objects.get_or_create(customer=customer,
                                                                                                area=area)
                        if sales_representative:
                            ic(sales_representative.name)
                            if sales_representative.name == 'AUTO':
                                ic('auto rep')
                                customer.is_auto_rep = True
                            ic(customer.is_auto_rep)
                            manufacturer_rep, created = ManufacturerRep.objects.get_or_create(customer=customer,
                                                                                                sales_rep_id=sales_representative.id)
                        customer.save()


                        messages.success(request, f'Customer {name} successfully created')
                        return redirect('create_customer')
                    except Exception as e:
                        ic(e)
                        if not Customer.objects.filter(customer_name=name).exists():
                            try:
                                Location.objects.get(id=location_instance.id).delete()
                            except:
                                pass
                        else:
                            try:
                                ic('custoemr remove')
                                customer_remove = Customer.objects.get(customer_name=name).delete()
                                ic(customer_remove)
                            except Exception as e:
                                ic(e)
                                pass
                        messages.error(request,
                                       'Exception occurred while creating the customer. Please submit the form again.')
                else:
                    Location.objects.get(id=location_instance.id).delete()
                    print('invalid form')
        else:
            customer_form = CustomerForm()
            location_form = LocationForm()
        customer_data = Customer.objects.exists()
        context_obj = SetupContext(model_search='customer', page_obj=customer_data, operation='create',
                                   segment='master-customer',location_form=location_form, customer_form=customer_form)
        context = context_obj.get_master_context()
        return render(request, 'billing/customer.html', context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def get_customer_modal(request):
    try:
        customer_data = Customer.objects.values('id', 'customer_name',
                                                'sh_name', 'print_name', 'email').order_by('customer_name')
        if request.method == 'POST':
            if 'submit_selected_record' in request.POST:
                id = request.POST['submit_selected_record']
                print(id)
                return redirect('update_customer', int(id))
            elif 'delete_selected_record' in request.POST:
                id = request.POST['delete_selected_record']
                model = Customer.objects.get(id=id)
                delete_models(request, model, name=model.customer_name)
                return redirect('create_customer')
            else:
                messages.info(request, 'No operation performed.')
                return redirect('create_customer')
        paginator = Paginator(customer_data, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context_obj = SetupContext(model_search='customer', page_obj=page_obj, operation='modal',
                                   segment='master-customer')
        context = context_obj.get_master_context()
        context['segment'] = 'master-customer'
        if not customer_data:
            messages.info(request, 'Records not found')
            return render(request, 'billing/customer.html', context=context)
        else:
            return render(request, 'billing/customer.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def update_customer(request, pk):
    try:
        try:
            customer_data = Customer.objects.get(id=pk)
            manufacturer_area = ManufacturerArea.objects.filter(customer=customer_data).first()
        except Exception as e:
            print(e)
            return render(request, 'billing/page-404.html')

        location_data, created = Location.objects.get_or_create(customer_location__id=pk)
        if customer_data.location is None:
            customer_data.location = location_data
            customer_data.save()
        if request.method == 'POST':
            location_form = LocationForm(request.POST, instance=location_data)
            customer_form = CustomerForm(request.POST, instance=customer_data)
            if location_form.is_valid():
                try:
                    location_instance = location_form.save()
                except Exception as e:
                    print(e)
                    location_instance = None
                    messages.error(request,
                                   'Exception occurred while creating the location. Please submit the form again.')
            else:
                location_instance = None
            if location_instance:
                if customer_form.is_valid():
                    name = customer_form.cleaned_data['customer_name']
                    area = customer_form.cleaned_data['area']
                    try:
                        customer = customer_form.save(commit=False)
                        customer.location = location_instance
                        customer.save()
                        if area != 'AUTO' and manufacturer_area.area.name == 'AUTO':
                            delete = ManufacturerArea.objects.filter(customer=customer_data).delete()
                        manufacturer_area, created = ManufacturerArea.objects.get_or_create(customer=customer,
                                                                                        area=area)

                        messages.info(request, f'Customer {name} updated.')
                        return redirect('create_customer')
                    except Exception as e:
                        if not Customer.objects.filter(customer_name=name).exists():
                            try:
                                Location.objects.get(id=location_instance.id).delete()
                            except:
                                pass
                        print(e)
                        messages.error(request,
                                       'Exception occurred while creating the manufacturer. Please submit the form again.')
                else:
                    Location.objects.get(id=location_instance.id).delete()
                    print('invalid form')
        else:

            location_form = LocationForm(instance=location_data)
            ic(manufacturer_area.area.name)
            if manufacturer_area.area.name != 'AUTO':
                customer_form = CustomerForm(instance=customer_data,initial={'area':manufacturer_area.area})
            else:
                customer_form = CustomerForm(instance=customer_data,initial={'area':manufacturer_area.area})

        context_obj = SetupContext(model_search='customer', page_obj=customer_data, operation='update',segment='master-customer',
        location_form = location_form,customer_form = customer_form)
        context = context_obj.get_master_context()
        return render(request, 'billing/customer.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def delete_customer(request):
    try:
        customer_data = Customer.objects.values('id', 'customer_name',
                                                'sh_name', 'print_name', 'email').order_by('customer_name')
        page_obj = pagination(request, customer_data)
        context_obj = SetupContext(model_search='customer_modal', page_obj=page_obj, operation='delete',segment='master-customer')
        context = context_obj.get_master_context()
        if not customer_data:
            messages.info(request, 'Records not found')
            return render(request, 'billing/customer.html', context=context)
        else:
            return render(request, 'billing/customer.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def view_customer(request):
    try:
        if request.method == 'POST':
            customer_name = request.POST.get('customer_name')
            if customer_name:
                customer_data = Customer.objects.filter(name__icontains=customer_name).order_by('-id')
            else:
                customer_data = Customer.objects.all().order_by('-id')
        else:
            customer_data = Customer.objects.all().order_by('-id')

        page_obj = pagination(request, customer_data)

        context_obj = SetupContext(model_search='customer', page_obj=page_obj, operation='view',segment='master-customer')
        context = context_obj.get_master_context()
        if not customer_data:
            messages.info(request, 'Records not found')
            return render(request, 'billing/customer.html', context=context)
        else:
            return render(request, 'billing/customer.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def setup_tax_structure(request):
    try:
        tax_type = 'sales_taxes'
        tax_structure_formset = TaxStructureFormSet()
        if request.method == 'GET':
            tax_type = request.GET.get('tax_type', '')
            if tax_type:
                tax_structure = TaxStructure.objects.filter(tax_type=tax_type).order_by('tax_id')
            else:
                tax_structure = TaxStructure.objects.filter(tax_type='sales_taxes').order_by('tax_id')
                ic(tax_structure)
            if tax_structure.count() < 10:
                tax_dictionary = {}
                tax_id = ['' for _ in range(10)]
                tax_desc = ['' for _ in range(10)]

                if tax_type == 'sales_taxes':
                    for i in range(10):
                        tax_id[i] = f'GST-S{i + 1:02}'
                        tax_desc[i] = f'SGST-{i + 1:02}-SGST/CGST/IGST'
                else:
                    for i in range(10):
                        tax_id[i] = f'GST-P{i + 1:02}'
                        tax_desc[i] = f'PGST-{i + 1:02}-SGST/CGST/IGST'

                for i in range(10):
                    tax_dictionary[i] = {'tax_type': tax_type, 'tax_id': tax_id[i], 'description': tax_desc[i]}
                bulk_tax_structure = [TaxStructure(**items) for items in tax_dictionary.values()]
                bulk_create = TaxStructure.objects.bulk_create(bulk_tax_structure)
                tax_structure_instance = TaxStructure.objects.filter(tax_type=tax_type)
                tax_structure_formset = TaxStructureFormSet(initial=tax_structure_instance.values())
            else:
                tax_structure_formset = TaxStructureFormSet(initial=tax_structure.values())
        elif request.method == 'POST':
            tax_type = request.GET.get('tax_type', '')
            tax_structure_formset = TaxStructureFormSet(request.POST)
            if tax_structure_formset.is_valid():
                try:
                    with transaction.atomic():
                        for i in range(10):
                            tax_id = request.POST.get(f'form-{i}-tax_id')
                            if tax_id:
                                tax_structure_instance = TaxStructure.objects.get(tax_id=tax_id)
                                sgst = request.POST.get(f'form-{i}-sgst')
                                cgst = request.POST.get(f'form-{i}-cgst')
                                igst = request.POST.get(f'form-{i}-igst')
                                description = request.POST.get(f'form-{i}-description')

                                tax_structure_instance.sgst = float(sgst) if sgst else None
                                tax_structure_instance.cgst = float(cgst) if cgst else None
                                tax_structure_instance.igst = float(igst) if igst else None
                                tax_structure_instance.description = description
                                tax_structure_instance.save()
                    messages.success(request, 'Tax Structure successfully updated.')
                except Exception as e:
                    print(e)
                    messages.error(request, 'Unable to update Tax Structure. Kindly contact support.')
            else:
                messages.error(request, 'Please correct the errors below.')

        context = {'tax_structure_formset': tax_structure_formset, 'label': 'Setup Tax Structure', 'tax_type': tax_type,
                   'segment': 'master-tax_structure'}
        return render(request, 'billing/tax_structure.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')


@measure_execution_time
def search_router(request, model_search):
    autocomplete_query = request.GET.get('autocomplete_query', '')
    manufacturer_modal_details = request.GET.get('manufacturer_modal_details', '')
    print(
        f'manufacturer_modal_details ::{manufacturer_modal_details},, modal_search: {model_search}, request:{request}')
    masterSearchObject = masterSearchEndpoint(request, model_search)

    if autocomplete_query:
        json_object = masterSearchObject.autocomplete_data()
        return json_object
    else:
        template, context = masterSearchObject.masterSearchRouter()
        return render(request, template, context)


@login_required(login_url="/login/")
@measure_execution_time
def setup_sales_rep(request):
    auto_rep = SalesRep.objects.get_or_create_model()
    data = SalesRep.objects.exists()
    form = SalesRepForm()
    if request.method == 'POST':
        form = SalesRepForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('setup_sales_rep')
    context_obj = SetupContext(model_search='sales_rep', operation='create',segment='master-selection-sales',
                               form=form,data=data,label='Setup Sales Representative')
    context = context_obj.get_selection_list_context()
    return render(request, 'billing/sales_rep.html', context=context)


@login_required(login_url="/login/")
@measure_execution_time
def view_sales_rep(request):
    data = SalesRep.objects.all().exclude(name='AUTO')
    page_obj = pagination(request, data)
    context_obj = SetupContext(model_search='sales_rep', operation='view', segment='master-selection-sales',
                               page_obj=page_obj,data=data, label='View Sales Representative')
    context = context_obj.get_selection_list_context()
    return render(request, 'billing/sales_rep.html', context=context)


@login_required(login_url="/login/")
@measure_execution_time
def update_sales_rep(request, pk):
    data = SalesRep.objects.get(id=pk)
    form = SalesRepForm(instance=data)
    if request.method == 'POST':
        form = SalesRepForm(request.POST, instance=data)

        if form.is_valid():
            form.save()
            return redirect('setup_sales_rep')
    context_obj = SetupContext(model_search='sales_rep', operation='update', segment='master-selection-sales',
                               form=form,data=data, label='Update Sales Representative')
    context = context_obj.get_selection_list_context()
    return render(request, 'billing/sales_rep.html', context=context)


@login_required(login_url="/login/")
@measure_execution_time
def get_sales_rep_modal(request):
    try:
        representative_data = SalesRep.objects.values('id', 'name', 'sh_name','mobile_number').order_by('name').exclude(name='AUTO')
        if request.method == 'POST':
            if 'submit_selected_record' in request.POST:
                id = request.POST['submit_selected_record']
                return redirect('update_sales_rep', int(id))
            elif 'delete_selected_record' in request.POST:
                id = request.POST['delete_selected_record']
                model = SalesRep.objects.get(id=id)
                delete_models(request, model, name=model.name)
                return redirect('setup_sales_rep')
            else:
                messages.info(request, 'No operation performed.')
                return redirect('create_manufacturer')
        page_obj = pagination(request, representative_data)
        context_obj = SetupContext(model_search='sales_rep', operation='modal',page_obj=page_obj, segment='master-selection-sales',
                                   data=representative_data, label='Update Sales Representative')
        context = context_obj.get_selection_list_context()

        if not representative_data:
            messages.info(request, 'Records not found')
            return render(request, 'billing/sales_rep.html', context=context)
        else:
            return render(request, 'billing/sales_rep.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def delete_sales_rep(request):
    try:
        representative_data = SalesRep.objects.values('id', 'name', 'sh_name','mobile_number').order_by('name').exclude(name='AUTO')
        page_obj = pagination(request, representative_data)
        context_obj = SetupContext(model_search='sales_rep', operation='delete', page_obj=page_obj,
                                   segment='master-selection-sales',
                                   data=representative_data, label='Delete Sales Representative')
        context = context_obj.get_selection_list_context()

        if not representative_data:
            messages.info(request, 'Records not found')
            return render(request, 'billing/sales_rep.html', context=context)
        else:
            return render(request, 'billing/sales_rep.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def setup_area(request):
    try:
        auto_area = Area.objects.get_or_create_model()
        data = Area.objects.exists()
        form = AreaForm()
        if request.method == 'POST':
            form = AreaForm(request.POST)

            if form.is_valid():
                form.save()
                return redirect('setup_area')
        context_obj = SetupContext(model_search='area', operation='create',segment='master-selection-area',
                                   form=form,data=data,label='Setup Area')
        context = context_obj.get_selection_list_context()
        return render(request, 'billing/area.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')

@login_required(login_url="/login/")
@measure_execution_time
def view_area(request):
    try:
        data = Area.objects.all().exclude(name='AUTO')
        ic(data)
        page_obj = pagination(request, data)
        context_obj = SetupContext(model_search='area', operation='view', segment='master-selection-area',
                                   page_obj=page_obj, data=data, label='View Area')
        context = context_obj.get_selection_list_context()
        return render(request, 'billing/area.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')

@login_required(login_url="/login/")
@measure_execution_time
def get_area_modal(request):
    try:
        data = Area.objects.values('id', 'name', 'pin_code', 'sh_name','area_status').order_by('-id').exclude(name='AUTO')
        if request.method == 'POST':
            if 'submit_selected_record' in request.POST:
                id = request.POST['submit_selected_record']
                return redirect('update_area', int(id))
            elif 'delete_selected_record' in request.POST:
                id = request.POST['delete_selected_record']
                model = Area.objects.get(id=id)
                delete_models(request, model, name=model.name)
                return redirect('setup_area')
            else:
                messages.info(request, 'No operation performed.')
                return redirect('setup_area')
        page_obj = pagination(request, data)
        context_obj = SetupContext(model_search='area', operation='modal', page_obj=page_obj,
                                   segment='master-selection-area',
                                   data=data, label='Update Area')
        context = context_obj.get_selection_list_context()
        ic(context)
        if not data:
            messages.info(request, 'Records not found')
            return render(request, 'billing/area.html', context=context)
        else:
            return render(request, 'billing/area.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')



@login_required(login_url="/login/")
@measure_execution_time
def update_area(request,pk):
    try:
        data = Area.objects.get(id=pk)
        form = AreaForm(instance=data)
        if request.method == 'POST':
            form = AreaForm(request.POST, instance=data)

            if form.is_valid():
                form.save()
                return redirect('setup_area')
        context_obj = SetupContext(model_search='area', operation='update', segment='master-selection-area',
                                   form=form, data=data, label='Update Area')
        context = context_obj.get_selection_list_context()
        return render(request, 'billing/area.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def delete_area(request):
    try:
        data = Area.objects.values('id', 'name', 'pin_code', 'sh_name','area_status').order_by('name').exclude(name='AUTO')
        page_obj = pagination(request, data)
        context_obj = SetupContext(model_search='area', operation='delete', page_obj=page_obj,
                                   segment='master-selection-area',
                                   data=data, label='Delete Area')
        context = context_obj.get_selection_list_context()

        if not data:
            messages.info(request, 'Records not found')
            return render(request, 'billing/area.html', context=context)
        else:
            return render(request, 'billing/area.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')



def create_missing_manufacturer_area(customer_instance):
    if isinstance(customer_instance,Customer):
        none_manufacturers = ManufacturerArea.objects.select_related('manufacturer', 'customer').filter(customer_id=customer_instance.id,manufacturer_id__isnull=True)
        if none_manufacturers.exists():
            delete = none_manufacturers.delete()
        existing_manufacturers = ManufacturerArea.objects.select_related('manufacturer', 'customer').filter(customer_id=customer_instance.id).\
            exclude(manufacturer_id = None).values_list('manufacturer_id',flat=True)
        missing_manufacturers = Manufacturer.objects.exclude(id__in=existing_manufacturers)
        if missing_manufacturers:
            for manufacturer in missing_manufacturers:
                manufacturer_creation = ManufacturerArea.objects.create(manufacturer=manufacturer,customer_id=customer_instance.id)
    else:
        raise TypeError(f"Invalid Keyword")


def create_missing_manufacturer_rep(customer_instance):
    if isinstance(customer_instance,Customer):
        none_manufacturers = ManufacturerRep.objects.select_related('manufacturer', 'customer').filter(customer_id=customer_instance.id,manufacturer_id__isnull=True)
        if none_manufacturers.exists():
            delete = none_manufacturers.delete()
        existing_manufacturers = ManufacturerRep.objects.select_related('manufacturer', 'customer').filter(customer_id=customer_instance.id).\
            exclude(manufacturer_id = None).values_list('manufacturer_id',flat=True)
        missing_manufacturers = Manufacturer.objects.exclude(id__in=existing_manufacturers)
        if missing_manufacturers:
            for manufacturer in missing_manufacturers:
                manufacturer_creation = ManufacturerRep.objects.create(manufacturer=manufacturer,customer_id=customer_instance.id)
    else:
        raise TypeError(f"Invalid Keyword")



@login_required(login_url="/login/")
@measure_execution_time
def setup_manufacturer_area(request):
    try:
        if not (Customer.objects.exists() and Manufacturer.objects.exists() and Area.objects.exists()):
            messages.info(request,'Kindly ensure Customer, Manufacturer, and Area is created.')
            context = {'flag': False, 'label': 'Setup Manufacturer Representative','segment':'master-selection-ma'}
            return render(request, 'billing/manufacturer_area.html', context=context)
        else:
            flag= True
        customer_id = request.GET.get('customer','')
        if customer_id:
            customer_instance = Customer.objects.get(id=customer_id)
            manufacturer_area = ManufacturerArea.objects.filter(customer_id=customer_instance.id)
            create_missing_manufacturer_area(customer_instance)
            manufacturer_data_form = ManufacturerAreaFormset(initial=manufacturer_area.values('id','manufacturer','area'))
            customer_form = CustomerDisplayForm(initial={'customer':(customer_id, customer_instance.customer_name)})
        else:
            customer_instance = Customer.objects.order_by('-id').first()
            create_missing_manufacturer_area(customer_instance)
            manufacturer_area = ManufacturerArea.objects.filter(customer_id=customer_instance.id)
            manufacturer_data_form = ManufacturerAreaFormset(initial=manufacturer_area.values('id','manufacturer','area'))
            customer_form = CustomerDisplayForm()
        if request.method == 'POST':
            saved_data = request.POST.dict()
            total = int(saved_data['form-TOTAL_FORMS'])
            try:
                with transaction.atomic():
                    for i in range(total):
                        area = saved_data.get(f'form-{i}-area','')
                        manufacturer = saved_data.get(f'form-{i}-manufacturer','')
                        if manufacturer:
                            manufacturer_area_queryset = ManufacturerArea.objects.get(customer_id=customer_instance.id,manufacturer_id=int(manufacturer))
                            if area:
                                manufacturer_area_queryset.area_id = int(area)
                                manufacturer_area_queryset.save()
                            else:
                                manufacturer_area_queryset.area = None
                                manufacturer_area_queryset.save()
                customer_form = CustomerDisplayForm(initial={'customer': (customer_instance.id, customer_instance.customer_name)})

                messages.success(request,f'Manufacturer|Area of {customer_instance.customer_name.upper()} is saved Successfully')
            except Exception as e:
                print(f"An error occurred: {e}")
                messages.error(request,'Exception occurred, Form not saved')
        context_obj = SetupContext(model_search='manufacturer_area', operation='create', segment='master-selection-ma',
                                   flag=flag,manufacturer_data_form=manufacturer_data_form,label='Setup Manufacturer Area',customer_form=customer_form)
        context = context_obj.get_selection_list_context()
        return render(request, 'billing/manufacturer_area.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def setup_manufacturer_rep(request):
    try:
        if not (Customer.objects.exists() and Manufacturer.objects.exists() and SalesRep.objects.exists()):
            messages.info(request,'Kindly ensure Customer, Manufacturer, and Sales Representative is created.')
            context = {'flag': False, 'label': 'Setup Manufacturer Representative','segment':'master-selection-mr'}
            return render(request, 'billing/manufacturer_rep.html', context=context)
        else:
            flag= True
        customer_id = request.GET.get('customer','')
        if customer_id:
            customer_instance = Customer.objects.get(id=customer_id)
            manufacturer_rep = ManufacturerRep.objects.filter(customer_id=customer_instance.id)
            create_missing_manufacturer_rep(customer_instance)
            manufacturer_data_form = ManufacturerRepFormset(initial=manufacturer_rep.values('id','manufacturer','sales_rep'))
            customer_form = CustomerDisplayForm(initial={'customer':(customer_id, customer_instance.customer_name)})
        else:
            customer_instance = Customer.objects.order_by('-id').first()
            create_missing_manufacturer_rep(customer_instance)
            manufacturer_rep = ManufacturerRep.objects.filter(customer_id=customer_instance.id)
            manufacturer_data_form = ManufacturerRepFormset(initial=manufacturer_rep.values('id','manufacturer','sales_rep'))
            customer_form = CustomerDisplayForm()
        if request.method == 'POST':
            saved_data = request.POST.dict()
            total = int(saved_data['form-TOTAL_FORMS'])
            try:
                with transaction.atomic():
                    for i in range(total):
                        sales_rep = saved_data.get(f'form-{i}-sales_rep','')
                        manufacturer = saved_data.get(f'form-{i}-manufacturer','')
                        if manufacturer:
                            manufacturer_rep_queryset = ManufacturerRep.objects.get(customer_id=customer_instance.id,manufacturer_id=int(manufacturer))
                            if sales_rep:
                                manufacturer_rep_queryset.sales_rep_id = int(sales_rep)
                                manufacturer_rep_queryset.save()
                            else:
                                manufacturer_rep_queryset.sales_rep = None
                                manufacturer_rep_queryset.save()
                customer_form = CustomerDisplayForm(initial={'customer': (customer_instance.id, customer_instance.customer_name)})
                messages.success(request,f'Manufacturer|Sales Rep of {customer_instance.customer_name.upper()} is saved Successfully')
            except Exception as e:
                print(f"An error occurred: {e}")
                messages.error(request,'Exception occurred, Form not saved')
        context_obj = SetupContext(model_search='manufacturer_rep', operation='create', segment='master-selection-mr',
                                   flag=flag,manufacturer_data_form=manufacturer_data_form,label='Setup Manufacturer Representative',customer_form=customer_form)
        context = context_obj.get_selection_list_context()
        return render(request, 'billing/manufacturer_rep.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def setup_carriers(request):
    try:
        data = Carriers.objects.exists()
        form = CarrierForm()
        if request.method == 'POST':
            form = CarrierForm(request.POST)

            if form.is_valid():
                form.save()
                return redirect('setup_carriers')
        context_obj = SetupContext(model_search='carriers', operation='create',segment='master-selection-carriers',
                                   form=form,data=data,label='Setup Carriers')
        context = context_obj.get_selection_list_context()
        return render(request, 'billing/carriers.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')

@login_required(login_url="/login/")
@measure_execution_time
def view_carriers(request):
    try:
        data = Carriers.objects.values('id', 'name', 'postal_code', 'sh_name', 'e_way_id').order_by('-id')
        page_obj = pagination(request, data)
        context_obj = SetupContext(model_search='carriers', operation='view', segment='master-selection-carriers',
                                   page_obj=page_obj, data=data, label='View Carriers')
        context = context_obj.get_selection_list_context()
        return render(request, 'billing/carriers.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')

@login_required(login_url="/login/")
@measure_execution_time
def update_carriers(request,pk):
    try:
        data = Carriers.objects.get(id=pk)
        form = CarrierForm(instance=data)
        if request.method == 'POST':
            form = CarrierForm(request.POST, instance=data)

            if form.is_valid():
                form.save()
                messages.success(request,f'Carrier {data.name} is updated Successfully.')
                return redirect('setup_carriers')
        context_obj = SetupContext(model_search='carriers', operation='update', segment='master-selection-carriers',
                                   form=form, data=data, label='Update Carriers')
        context = context_obj.get_selection_list_context()
        return render(request, 'billing/carriers.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')

@login_required(login_url="/login/")
@measure_execution_time
def delete_carriers(request):
    try:
        data = Carriers.objects.values('id', 'name', 'postal_code', 'sh_name', 'e_way_id').order_by('-id')

        page_obj = pagination(request, data)
        context_obj = SetupContext(model_search='carriers', operation='delete', page_obj=page_obj,
                                   segment='master-selection-carriers',
                                   data=data, label='Delete Area')
        context = context_obj.get_selection_list_context()

        if not data:
            messages.info(request, 'Records not found')
            return render(request, 'billing/carriers.html', context=context)
        else:
            return render(request, 'billing/carriers.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')

@login_required(login_url="/login/")
@measure_execution_time
def get_carriers_modal(request):
    try:
        data = Carriers.objects.values('id', 'name', 'postal_code', 'sh_name', 'e_way_id').order_by('-id')
        if request.method == 'POST':
            if 'submit_selected_record' in request.POST:
                id = request.POST['submit_selected_record']
                return redirect('update_carriers', int(id))
            elif 'delete_selected_record' in request.POST:
                id = request.POST['delete_selected_record']
                model = Carriers.objects.get(id=id)
                delete_models(request, model, name=model.name)
                return redirect('setup_carriers')
            else:
                messages.info(request, 'No operation performed.')
                return redirect('setup_carriers')
        page_obj = pagination(request, data)
        context_obj = SetupContext(model_search='carriers', operation='modal', page_obj=page_obj,
                                   segment='master-selection-carriers',
                                   data=data, label='Update Carriers')
        context = context_obj.get_selection_list_context()
        if not data:
            messages.info(request, 'Records not found')
            return render(request, 'billing/carriers.html', context=context)
        else:
            return render(request, 'billing/carriers.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')

@login_required(login_url="/login/")
@measure_execution_time
def setup_units(request):
    try:
        data = Units.objects.exists()
        form = GeneralSelectionListForm()
        ic(form)
        if request.method == 'POST':
            form = GeneralSelectionListForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data.get('name','')
                sh_name = form.cleaned_data.get('sh_name','')
                unit = Units.objects.create(name=name,sh_name=sh_name)
                messages.success(request, f'Unit {unit.name} is created Successfully.')

                return redirect('setup_units')
        context_obj = SetupContext(model_search='units', operation='create',segment='master-selection-unit',
                                   form=form,data=data,label='Setup Units')
        context = context_obj.get_selection_list_context()
        return render(request, 'billing/unit.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')

@login_required(login_url="/login/")
@measure_execution_time
def view_units(request):
    try:
        data = Units.objects.values().order_by('-id')
        page_obj = pagination(request, data)
        context_obj = SetupContext(model_search='units', operation='view', segment='master-selection-units',
                                   page_obj=page_obj, data=data, label='View Units')
        context = context_obj.get_selection_list_context()
        return render(request, 'billing/unit.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')

@login_required(login_url="/login/")
@measure_execution_time
def update_units(request,pk):
    try:
        data = Units.objects.get(id=pk)
        form = GeneralSelectionListForm(initial={'name':data.name,'sh_name':data.sh_name})
        if request.method == 'POST':
            form = GeneralSelectionListForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data.get('name', '')
                sh_name = form.cleaned_data.get('sh_name', '')
                data.name = name
                data.sh_name = sh_name
                data.save()
                messages.success(request,f'Unit {data.name} is updated Successfully.')
                return redirect('setup_units')
        context_obj = SetupContext(model_search='units', operation='update', segment='master-selection-units',
                                   form=form, data=data, label='Update Unit')
        context = context_obj.get_selection_list_context()
        return render(request, 'billing/unit.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')

@login_required(login_url="/login/")
@measure_execution_time
def delete_units(request):
    try:
        data = Units.objects.values().order_by('-id')
        page_obj = pagination(request, data)
        context_obj = SetupContext(model_search='units', operation='delete', page_obj=page_obj,
                                   segment='master-selection-units',
                                   data=data, label='Delete Unit')
        context = context_obj.get_selection_list_context()
        if not data:
            messages.info(request, 'Records not found')
            return render(request, 'billing/unit.html', context=context)
        else:
            return render(request, 'billing/unit.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')

@login_required(login_url="/login/")
@measure_execution_time
def get_units_modal(request):
    try:
        data = Units.objects.values().order_by('-id')
        if request.method == 'POST':
            if 'submit_selected_record' in request.POST:
                id = request.POST['submit_selected_record']
                return redirect('update_units', int(id))
            elif 'delete_selected_record' in request.POST:
                id = request.POST['delete_selected_record']
                model = Units.objects.get(id=id)
                delete_models(request, model, name=model.name)
                return redirect('setup_units')
            else:
                messages.info(request, 'No operation performed.')
                return redirect('setup_units')
        page_obj = pagination(request, data)
        context_obj = SetupContext(model_search='units', operation='modal', page_obj=page_obj,
                                   segment='master-selection-units',
                                   data=data, label='Update Unit')
        context = context_obj.get_selection_list_context()
        ic(context)
        if not data:
            messages.info(request, 'Records not found')
            return render(request, 'billing/unit.html', context=context)
        else:
            return render(request, 'billing/unit.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')

@login_required(login_url="/login/")
@measure_execution_time
def setup_departments(request):
    try:
        data = Departments.objects.exists()
        form = GeneralSelectionListForm()
        if request.method == 'POST':
            form = GeneralSelectionListForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data.get('name', '')
                sh_name = form.cleaned_data.get('sh_name', '')
                Departments.objects.create(name=name,sh_name=sh_name)
                return redirect('setup_departments')
        context_obj = SetupContext(model_search='departments', operation='create',segment='master-selection-departments',
                                   form=form,data=data,label='Setup Departments')
        context = context_obj.get_selection_list_context()
        return render(request, 'billing/departments.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')

@login_required(login_url="/login/")
@measure_execution_time
def view_departments(request):
    try:
        data = Departments.objects.values().order_by('-id')
        page_obj = pagination(request, data)
        context_obj = SetupContext(model_search='departments', operation='view', segment='master-selection-departments',
                                   page_obj=page_obj, data=data, label='View Departments')
        context = context_obj.get_selection_list_context()
        return render(request, 'billing/departments.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')

@login_required(login_url="/login/")
@measure_execution_time
def update_departments(request,pk):
    try:
        data = Departments.objects.get(id=pk)
        form = GeneralSelectionListForm(initial={'name':data.name,'sh_name':data.sh_name})
        if request.method == 'POST':
            form = GeneralSelectionListForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data.get('name', '')
                sh_name = form.cleaned_data.get('sh_name', '')
                data.name = name
                data.sh_name = sh_name
                data.save()
                messages.success(request,f'Department {data.name} is updated Successfully.')
                return redirect('setup_departments')
        context_obj = SetupContext(model_search='departments', operation='update', segment='master-selection-departments',
                                   form=form, data=data, label='Update Departments')
        context = context_obj.get_selection_list_context()
        return render(request, 'billing/departments.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')

@login_required(login_url="/login/")
@measure_execution_time
def delete_departments(request):
    try:
        data = Departments.objects.values().order_by('-id')
        page_obj = pagination(request, data)
        context_obj = SetupContext(model_search='departments', operation='delete', page_obj=page_obj,
                                   segment='master-selection-departments',
                                   data=data, label='Delete Departments')
        context = context_obj.get_selection_list_context()
        if not data:
            messages.info(request, 'Records not found')
            return render(request, 'billing/departments.html', context=context)
        else:
            return render(request, 'billing/departments.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')

@login_required(login_url="/login/")
@measure_execution_time
def get_departments_modal(request):
    try:
        data = Departments.objects.values().order_by('-id')
        if request.method == 'POST':
            if 'submit_selected_record' in request.POST:
                id = request.POST['submit_selected_record']
                return redirect('update_departments', int(id))
            elif 'delete_selected_record' in request.POST:
                id = request.POST['delete_selected_record']
                model = Departments.objects.get(id=id)
                delete_models(request, model, name=model.name)
                return redirect('setup_departments')
            else:
                messages.info(request, 'No operation performed.')
                return redirect('setup_departments')
        page_obj = pagination(request, data)
        context_obj = SetupContext(model_search='departments', operation='modal', page_obj=page_obj,
                                   segment='master-selection-departments',
                                   data=data, label='Update Departments')
        context = context_obj.get_selection_list_context()
        if not data:
            messages.info(request, 'Records not found')
            return render(request, 'billing/departments.html', context=context)
        else:
            return render(request, 'billing/departments.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def setup_division(request):
    try:
        data = Division.objects.exists()
        form = DivisionForm()
        if request.method == 'POST':
            form = DivisionForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('setup_division')
        context_obj = SetupContext(model_search='division', operation='create',segment='master-selection-division',
                                   form=form,data=data,label='Setup Division')
        context = context_obj.get_selection_list_context()
        return render(request, 'billing/division.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')

@login_required(login_url="/login/")
@measure_execution_time
def view_division(request):
    try:
        data = Division.objects.values('id','name','sh_name','division_id','customer__customer_name').order_by('-id')
        page_obj = pagination(request, data)
        context_obj = SetupContext(model_search='division', operation='view', segment='master-selection-division',
                                   page_obj=page_obj, data=data, label='View Division')
        context = context_obj.get_selection_list_context()
        return render(request, 'billing/division.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')

@login_required(login_url="/login/")
@measure_execution_time
def update_division(request,pk):
    try:
        data = Division.objects.get(id=pk)
        form = DivisionForm(instance=data)
        if request.method == 'POST':
            form = DivisionForm(request.POST, instance=data)
            if form.is_valid():
                form.save()
                messages.success(request,f'Division {data.name} is updated Successfully.')
                return redirect('setup_division')
        context_obj = SetupContext(model_search='division', operation='update', segment='master-selection-division',
                                   form=form, data=data, label='Update Division')
        context = context_obj.get_selection_list_context()
        return render(request, 'billing/division.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')

@login_required(login_url="/login/")
@measure_execution_time
def delete_division(request):
    try:
        data = Division.objects.values('id','name','sh_name','division_id','customer__customer_name').order_by('-id')
        page_obj = pagination(request, data)
        context_obj = SetupContext(model_search='division', operation='delete', page_obj=page_obj,
                                   segment='master-selection-division',
                                   data=data, label='Delete Division')
        context = context_obj.get_selection_list_context()
        if not data:
            messages.info(request, 'Records not found')
            return render(request, 'billing/division.html', context=context)
        else:
            return render(request, 'billing/division.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')

@login_required(login_url="/login/")
@measure_execution_time
def get_division_modal(request):
    try:
        data = Division.objects.values('id','name','sh_name','division_id','customer__customer_name').order_by('-id')
        if request.method == 'POST':
            if 'submit_selected_record' in request.POST:
                id = request.POST['submit_selected_record']
                return redirect('update_division', int(id))
            elif 'delete_selected_record' in request.POST:
                id = request.POST['delete_selected_record']
                model = Division.objects.get(id=id)
                delete_models(request, model, name=model.name)
                return redirect('setup_division')
            else:
                messages.info(request, 'No operation performed.')
                return redirect('setup_division')
        page_obj = pagination(request, data)
        context_obj = SetupContext(model_search='division', operation='modal', page_obj=page_obj,
                                   segment='master-selection-division',
                                   data=data, label='Update Division')
        context = context_obj.get_selection_list_context()
        if not data:
            messages.info(request, 'Records not found')
            return render(request, 'billing/division.html', context=context)
        else:
            return render(request, 'billing/division.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def setup_discount_class(request):
    try:
        data = DiscountClass.objects.exists()
        form = GeneralSelectionListForm()
        if request.method == 'POST':
            form = GeneralSelectionListForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data.get('name', '')
                sh_name = form.cleaned_data.get('sh_name', '')
                discount = DiscountClass.objects.create(name=name, sh_name=sh_name)
                messages.success(request,f'Discount Class {discount.name} created successfully')
                return redirect('setup_discount_class')
        context_obj = SetupContext(model_search='discount_class', operation='create',segment='master-selection-discount_class',
                                   form=form,data=data,label='Setup Discount Class')
        context = context_obj.get_selection_list_context()
        return render(request, 'billing/discount_class.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')

@login_required(login_url="/login/")
@measure_execution_time
def view_discount_class(request):
    try:
        data = DiscountClass.objects.values().order_by('-id')
        page_obj = pagination(request, data)
        context_obj = SetupContext(model_search='discount_class', operation='view', segment='master-selection-discount_class',
                                   page_obj=page_obj, data=data, label='View Discount Class')
        context = context_obj.get_selection_list_context()
        return render(request, 'billing/discount_class.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')

@login_required(login_url="/login/")
@measure_execution_time
def update_discount_class(request,pk):
    try:
        data = DiscountClass.objects.get(id=pk)
        form = GeneralSelectionListForm(initial={'name':data.name,'sh_name':data.sh_name})
        if request.method == 'POST':
            form = GeneralSelectionListForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data.get('name', '')
                sh_name = form.cleaned_data.get('sh_name', '')
                data.name = name
                data.sh_name= sh_name
                data.save()
                messages.success(request,f'Discount Class {data.name} is updated Successfully.')
                return redirect('setup_discount_class')
        context_obj = SetupContext(model_search='discount_class', operation='update', segment='master-selection-discount_class',
                                   form=form, data=data, label='Update Discount Class')
        context = context_obj.get_selection_list_context()
        return render(request, 'billing/discount_class.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')

@login_required(login_url="/login/")
@measure_execution_time
def delete_discount_class(request):
    try:
        data = DiscountClass.objects.values().order_by('-id')
        page_obj = pagination(request, data)
        context_obj = SetupContext(model_search='discount_class', operation='delete', page_obj=page_obj,
                                   segment='master-selection-discount_class',
                                   data=data, label='Delete Discount Class')
        context = context_obj.get_selection_list_context()
        if not data:
            messages.info(request, 'Records not found')
            return render(request, 'billing/discount_class.html', context=context)
        else:
            return render(request, 'billing/discount_class.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')

@login_required(login_url="/login/")
@measure_execution_time
def get_discount_class_modal(request):
    try:
        data = DiscountClass.objects.values().order_by('-id')
        if request.method == 'POST':
            if 'submit_selected_record' in request.POST:
                id = request.POST['submit_selected_record']
                return redirect('update_discount_class', int(id))
            elif 'delete_selected_record' in request.POST:
                id = request.POST['delete_selected_record']
                model = DiscountClass.objects.get(id=id)
                delete_models(request, model, name=model.name)
                return redirect('setup_discount_class')
            else:
                messages.info(request, 'No operation performed.')
                return redirect('setup_discount_class')
        page_obj = pagination(request, data)
        context_obj = SetupContext(model_search='discount_class', operation='modal', page_obj=page_obj,
                                   segment='master-selection-discount_class',
                                   data=data, label='Update Discount Class')
        context = context_obj.get_selection_list_context()
        if not data:
            messages.info(request, 'Records not found')
            return render(request, 'billing/discount_class.html', context=context)
        else:
            return render(request, 'billing/discount_class.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def setup_customer_class(request):
    try:
        data = DiscountClass.objects.exists()
        form = GeneralSelectionListForm()
        if request.method == 'POST':
            form = GeneralSelectionListForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data.get('name', '')
                sh_name = form.cleaned_data.get('sh_name', '')
                discount = DiscountClass.objects.create(name=name, sh_name=sh_name)
                messages.success(request,f'Customer Class {discount.name} created successfully')
                return redirect('setup_customer_class')
        context_obj = SetupContext(model_search='customer_class', operation='create',segment='master-selection-customer_class',
                                   form=form,data=data,label='Setup Customer Class')
        context = context_obj.get_selection_list_context()
        return render(request, 'billing/customer_class.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')

@login_required(login_url="/login/")
@measure_execution_time
def view_customer_class(request):
    try:
        data = DiscountClass.objects.values().order_by('-id')
        page_obj = pagination(request, data)
        context_obj = SetupContext(model_search='customer_class', operation='view', segment='master-selection-customer_class',
                                   page_obj=page_obj, data=data, label='View Customer Class')
        context = context_obj.get_selection_list_context()
        return render(request, 'billing/customer_class.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')

@login_required(login_url="/login/")
@measure_execution_time
def update_customer_class(request,pk):
    try:
        data = DiscountClass.objects.get(id=pk)
        form = GeneralSelectionListForm(initial={'name':data.name,'sh_name':data.sh_name})
        if request.method == 'POST':
            form = GeneralSelectionListForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data.get('name', '')
                sh_name = form.cleaned_data.get('sh_name', '')
                data.name = name
                data.sh_name= sh_name
                data.save()
                messages.success(request,f'Customer Class {data.name} is updated Successfully.')
                return redirect('setup_customer_class')
        context_obj = SetupContext(model_search='customer_class', operation='update', segment='master-selection-customer_class',
                                   form=form, data=data, label='Update Customer Class')
        context = context_obj.get_selection_list_context()
        return render(request, 'billing/customer_class.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')

@login_required(login_url="/login/")
@measure_execution_time
def delete_customer_class(request):
    try:
        data = DiscountClass.objects.values().order_by('-id')
        page_obj = pagination(request, data)
        context_obj = SetupContext(model_search='customer_class', operation='delete', page_obj=page_obj,
                                   segment='master-selection-customer_class',
                                   data=data, label='Delete Customer Class')
        context = context_obj.get_selection_list_context()
        if not data:
            messages.info(request, 'Records not found')
            return render(request, 'billing/customer_class.html', context=context)
        else:
            return render(request, 'billing/customer_class.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')

@login_required(login_url="/login/")
@measure_execution_time
def get_customer_class_modal(request):
    try:
        data = DiscountClass.objects.values().order_by('-id')
        if request.method == 'POST':
            if 'submit_selected_record' in request.POST:
                id = request.POST['submit_selected_record']
                return redirect('update_customer_class', int(id))
            elif 'delete_selected_record' in request.POST:
                id = request.POST['delete_selected_record']
                model = DiscountClass.objects.get(id=id)
                delete_models(request, model, name=model.name)
                return redirect('setup_customer_class')
            else:
                messages.info(request, 'No operation performed.')
                return redirect('setup_customer_class')
        page_obj = pagination(request, data)
        context_obj = SetupContext(model_search='customer_class', operation='modal', page_obj=page_obj,
                                   segment='master-selection-customer_class',
                                   data=data, label='Update Customer Class')
        context = context_obj.get_selection_list_context()
        if not data:
            messages.info(request, 'Records not found')
            return render(request, 'billing/customer_class.html', context=context)
        else:
            return render(request, 'billing/customer_class.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')

