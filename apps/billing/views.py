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
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.urls import reverse
from icecream import ic

from apps.billing.services.decorators import measure_execution_time
from apps.billing.form import ManufacturerForm, ProductForm, ReceiptForm, GroupForm, CustomerForm, SignUpForm, \
    LoginForm, LocationForm, TaxDetailForm, TaxStructureForm
from django.shortcuts import render, redirect
from apps.billing.models import Manufacturer, Product, Receipt, ReceiptProduct, ProductGroup, Customer, CustomUser, \
    Location, TaxDetail, TaxStructure
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
    print(f'TaxDetail:{TaxDetail.objects.count()}, TaxStructure: {TaxStructure.objects.count()}')
    html_template = loader.get_template('billing/dashboard.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
@measure_execution_time
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    # try:
    load_template = request.path.split('/')[-1]
    if load_template == 'admin':
        return HttpResponseRedirect(reverse('admin:index'))
    context['segment'] = load_template
    ic(context)
    html_template = loader.get_template('billing/' + load_template)
    return HttpResponse(html_template.render(context, request))

    # except template.TemplateDoesNotExist:
    #     return render(request, 'billing/page-404.html')
    # except:
    #     return render(request, 'billing/page-500.html')


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
            messages.error(request, f'Invalid Form: {form.errors}')

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
            messages.error(request, f'Invalid Form: {form.errors}')
            return redirect('register')
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
    context_obj = SetupContext(model_search='manufacturer', page_obj=master_data, operation='create')
    context = context_obj.get_context()
    context['manufacturer_form'] = manufacturer_form
    context['location_form'] = location_form
    return render(request, 'billing/manufacturer.html', context)
    # except template.TemplateDoesNotExist:
    #     return render(request, 'billing/page-404.html')
    # except:
    #     return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def get_manufacturer_modal(request):
    # try:
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
    context_obj = SetupContext(model_search='manufacturer_modal', page_obj=page_obj, operation='modal')
    context = context_obj.get_context()

    if not manufacturer_data:
        messages.info(request, 'Records not found')
        return render(request, 'billing/manufacturer.html', context=context)
    else:
        return render(request, 'billing/manufacturer.html', context=context)  # except template.TemplateDoesNotExist:
    #     return render(request,'billing/page-404.html')
    # except:
    #     return render(request,'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def update_manufacturer(request, pk):
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
                messages.error(request, 'Exception occurred while creating the location. Please submit the form again.')
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
    context_obj = SetupContext(model_search='manufacturer', page_obj=manufacturer_data, operation='update')
    context = context_obj.get_context()
    context['manufacturer_form'] = manufacturer_form
    context['location_form'] = location_form
    return render(request, 'billing/manufacturer.html', context=context)
    # except template.TemplateDoesNotExist:
    #     return render(request, 'billing/page-404.html')
    # except:
    #     return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def delete_manufacturer(request):
    # try:
    manufacturer_data = Manufacturer.objects.annotate(
        product_count=Count('product_manufacturer')
    ).values(
        'id', 'name', 'type', 'sh_name', 'print_name', 'product_count'
    ).order_by('name')
    if request.method == 'POST':
        if 'delete_selected_record' in request.POST:
            pk = request.POST['delete_selected_record']
            manufacturer = Manufacturer.objects.get(id=pk)
            name = manufacturer.name
            delete_models(request, manufacturer, name)
            return redirect('create_manufacturer')
        else:
            messages.error(request, 'Selected record does not exist in Database')
            return redirect('delete_manufacturer')
    page_obj = pagination(request, manufacturer_data)
    context_obj = SetupContext(model_search='manufacturer_modal', page_obj=page_obj, operation='delete')
    context = context_obj.get_context()
    if not manufacturer_data:
        messages.info(request, 'Records not found')
        return render(request, 'billing/manufacturer.html', context=context)
    else:
        return render(request, 'billing/manufacturer.html', context=context)
    # except template.TemplateDoesNotExist:
    #     return render(request, 'billing/page-404.html')
    # except:
    #     return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def view_manufacturer(request):
    # try:
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
    context_obj = SetupContext(model_search='manufacturer', page_obj=page_obj, operation='view')
    context = context_obj.get_context()
    if not manufacturer_data:
        messages.info(request, 'Records not found')
        return render(request, 'billing/manufacturer.html', context=context)
    else:
        return render(request, 'billing/manufacturer.html', context=context)
    # except template.TemplateDoesNotExist:
    #     return render(request, 'billing/page-404.html')
    # except:
    #     return render(request, 'billing/page-500.html')


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
        context_obj = SetupContext(model_search='product', page_obj=product_data, operation='create')
        context = context_obj.get_context()
        context['form'] = form
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
            values('id', 'product_name', 'product_code',
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
        context_obj = SetupContext(model_search='product_model', page_obj=page_obj, operation='modal')
        context = context_obj.get_context()
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
            values('id', 'product_name', 'product_code',
                   'manufacturer__name', 'buy_rate', 'sell_rate').order_by('product_name')
        if request.method == 'POST':
            if 'delete_selected_record' in request.POST:
                pk = request.POST['delete_selected_record']
                product = Product.objects.get(id=pk)
                name = product.product_name
                delete_models(request, product, name)
                return redirect('create_product')
            else:
                messages.error(request, 'Selected record does not exist in Database')
                return redirect('delete_product')
        page_obj = pagination(request, product_data)
        context_obj = SetupContext(model_search='product_modal', page_obj=page_obj, operation='delete')
        context = context_obj.get_context()
        print('context:', context)
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
    # try:
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
    context_obj = SetupContext(model_search='product', page_obj=product_data, operation='update')
    context = context_obj.get_context()
    context['form'] = form
    return render(request, 'billing/products.html', context=context)
    # except template.TemplateDoesNotExist:
    #     return render(request, 'billing/page-404.html')
    # except:
    #     return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def view_product(request):
    try:
        query = ''
        results = Product.objects.select_related('manufacturer').values(
            'id', 'product_name', 'product_code', 'manufacturer__name', 'buy_rate', 'sell_rate',
            'manufacturer', 'buy_rate', 'sell_rate').order_by('product_name')
        page_obj = pagination(request, results)
        context_obj = SetupContext(model_search='product', page_obj=page_obj, operation='view')
        context = context_obj.get_context()
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

        context = {'form': form, 'flag': 'modal'}
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
        context_obj = SetupContext(model_search='group', page_obj=group_data, operation='create')
        context = context_obj.get_context()
        context['form'] = form
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
        context_obj = SetupContext(model_search='group', page_obj=page_obj, operation='view')
        context = context_obj.get_context()
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
        context_obj = SetupContext(model_search='group', page_obj=page_obj, operation='modal')
        context = context_obj.get_context()
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
        context_obj = SetupContext(model_search='group', page_obj=group_data, operation='update')
        context = context_obj.get_context()
        context['form'] = form
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
        if request.method == 'POST':
            if 'delete_selected_record' in request.POST:
                pk = request.POST['delete_selected_record']
                group = ProductGroup.objects.get(id=pk)
                name = group.group_name
                delete_models(request, group, name)
                return redirect('create_group')
            else:
                messages.error(request, 'Selected record does not exist in Database')
                return redirect('delete_group')
        page_obj = pagination(request, group_data)
        context_obj = SetupContext(model_search='group_modal', page_obj=page_obj, operation='delete')
        context = context_obj.get_context()
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
                    messages.error(request, 'Exception occurred while creating the location. Please submit the form again.')
            else:
                location_instance = None
            if location_instance:
                if customer_form.is_valid():
                    name = customer_form.cleaned_data['customer_name']
                    try:
                        customer = customer_form.save(commit=True)
                        customer.location = location_instance
                        customer.save()
                        messages.success(request, f'Customer {name} successfully created')
                        return redirect('create_customer')
                    except Exception as e:
                        if not Customer.objects.filter(customer_name=name).exists():
                            try:
                                Location.objects.get(id=location_instance.id).delete()
                            except:
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
        context_obj = SetupContext(model_search='customer', page_obj=customer_data, operation='create')
        context = context_obj.get_context()
        context['customer_form'] = customer_form
        context['location_form'] = location_form
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
        context_obj = SetupContext(model_search='customer', page_obj=page_obj, operation='modal')
        context = context_obj.get_context()
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
                    try:
                        customer = customer_form.save(commit=False)
                        customer.location = location_instance
                        customer.save()
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
            customer_form = CustomerForm(instance=customer_data)

        context_obj = SetupContext(model_search='customer', page_obj=customer_data, operation='update')
        context = context_obj.get_context()
        context['location_form'] = location_form
        context['customer_form'] = customer_form
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
        if request.method == 'POST':
            if 'delete_selected_record' in request.POST:
                pk = request.POST['delete_selected_record']
                customer = Customer.objects.get(id=pk)
                name = customer.customer_name
                delete_models(request, customer, name)
                return redirect('create_customer')
            else:
                messages.error(request, 'Selected record does not exist in Database')
                return redirect('delete_customer')
        page_obj = pagination(request, customer_data)
        context_obj = SetupContext(model_search='customer_modal', page_obj=page_obj, operation='delete')
        context = context_obj.get_context()
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
                customer_data = Customer.objects.filter(name__icontains=customer_name).order_by('customer_name')
            else:
                customer_data = Customer.objects.all().order_by('customer_name')
        else:
            customer_data = Customer.objects.all().order_by('customer_name')

        page_obj = pagination(request, customer_data)

        context_obj = SetupContext(model_search='customer', page_obj=page_obj, operation='view')
        context = context_obj.get_context()
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
        tax_structure_form = TaxStructureForm()
        flag = False
        new_tax_id = ''
        if request.method == 'POST':
            tax_structure_form = TaxStructureForm(request.POST)
            tax_details_form = TaxDetailForm(request.POST)
            flag=True
            new_tax_id = request.POST.get('new_tax_id','')
            if tax_structure_form.is_valid():
                try:
                    tax_structure_instance = tax_structure_form.save()
                    ic(tax_structure_instance)
                except Exception as e:
                    print(e)
                    tax_structure_instance = None
                    messages.error(request, 'Exception occurred while creating the Tax Structure. Please submit the form again.')
            else:
                tax_structure_instance = None
            if tax_structure_instance:
                if tax_details_form.is_valid():
                    try:
                        tax_details = tax_details_form.save(commit=False)
                        tax_details.tax_structure = tax_structure_instance
                        tax_details.tax_id = new_tax_id
                        if not tax_details.description:
                            tax_details.description = new_tax_id
                        tax_details.save()
                        messages.success(request,f'Tax Structure {tax_details.tax_id} Successfully Created')
                        return redirect('setup_tax_structure')
                    except IntegrityError:
                        messages.error(request, f'A record with {new_tax_id} Tax ID already exists,Kindly delete the existing Tax ID')
                        if not TaxDetail.objects.filter(tax_id=new_tax_id).exists():
                            try:
                                tax_structure_instance.delete()
                            except:
                                pass
                        return redirect('setup_tax_structure')
                    except Exception as e:
                        print(e)
                        if not TaxDetail.objects.filter(tax_id=new_tax_id).exists():
                            try:
                                tax_structure_instance.delete()
                            except:
                                pass
                            messages.error(request,
                                           'Exception occurred while creating the Tax Details. Please submit the form again.')
                            redirect('setup_tax_structure')
                else:
                    TaxStructure.objects.get(id=tax_structure_instance.id).delete()
                    print('invalid form')


        elif request.method == 'GET':
            tax_category = request.GET.get('tax_category', '')
            tax_type = request.GET.get('tax_type', '')
            if tax_category and tax_type:
                tax_structure_form = TaxStructureForm(request.GET)
                last_tax = (TaxDetail.objects.filter(Q(tax_structure__tax_type=tax_type) & Q(tax_structure__tax_category=tax_category))
                            .order_by('-id').first())
                prefix = 'SGST' if 'sgst' in tax_type else 'IGST'
                if last_tax:
                    tax_id = last_tax.tax_id
                    if tax_id:
                        if tax_category == 'sales_taxes':
                            sl_no = tax_id.split('-S')[1]
                            suffix = int(sl_no) + 1
                            if suffix <=9:
                                new_tax_id = f'{prefix.strip()}-S0{suffix}'
                            else:
                                new_tax_id = f'{prefix.strip()}-S{suffix}'
                        else:
                            sl_no = tax_id.split('-P')[1]
                            suffix = int(sl_no) + 1
                            if suffix <=9:
                                new_tax_id = f'{prefix.strip()}-P0{suffix}'
                            else:
                                new_tax_id = f'{prefix.strip()}-P{suffix}'
                    else:
                        messages.error(request,'Remove previously created TAX Structure')
                else:
                    if tax_category == 'sales_taxes':
                        new_tax_id = f'{prefix.strip()}-S01'
                    else:
                        new_tax_id = f'{prefix.strip()}-P01'
                flag = True
        initial_data = {'description': new_tax_id}
        tax_details_form = TaxDetailForm(initial=initial_data)
        context = {'tax_details_form': tax_details_form, 'tax_structure_form': tax_structure_form, 'flag': flag,
                   'new_tax_id': new_tax_id, 'label': 'Setup Tax Structure','operation':'create'}
        return render(request, 'billing/tax_structure.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')

@login_required(login_url="/login/")
@measure_execution_time
def view_tax_structure(request):
    try:
        tax_structure_form = TaxStructureForm()
        if request.method == 'GET':
            tax_category = request.GET.get('tax_category', '')
            tax_type = request.GET.get('tax_type', '')

            if tax_category and tax_type:
                tax_structure_form = TaxStructureForm(request.GET)
                tax_structures = TaxStructure.objects.prefetch_related('tax_details').filter(
                    Q(tax_category=tax_category) & Q(tax_type=tax_type)).order_by('-id')
            else:
                tax_structures = TaxStructure.objects.prefetch_related('tax_details').order_by('tax_details__tax_id')
        else:
            tax_structures = TaxStructure.objects.prefetch_related('tax_details').order_by('tax_details__tax_id')

        tax_structures = tax_structures
        context = {'tax_structures':tax_structures,'tax_structure_form':tax_structure_form,'label':'View Tax Structure','operation':'view'}
        if not tax_structures:
            messages.info(request, 'Records not found')
            return render(request, 'billing/tax_structure.html', context=context)
        else:
            return render(request, 'billing/tax_structure.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'billing/page-404.html')
    except:
        return render(request, 'billing/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def update_tax_structure(request,pk):
    # try:
    tax_details = TaxDetail.objects.get(id=pk)
    tax_details_form = TaxDetailForm(instance=tax_details)
    tax_structures = TaxStructure.objects.get(id=tax_details.tax_structure.id)
    if request.method == 'POST':
        tax_details_form = TaxDetailForm(request.POST,instance=tax_details)
        if tax_details_form.is_valid():
            try:
                tax_details = tax_details_form.save()
                messages.success(request, f'Tax Structure {tax_details.tax_id} Successfully Updated')
                return redirect('view_tax_structure')
            except Exception as e:
                print(e)
                messages.error(request,
                               'Exception occurred while update the Tax Details.TAX Not Updated')
                redirect('setup_tax_structure')
        else:
            print('invalid form')
    context = {'tax_structures': tax_structures, 'tax_details_form': tax_details_form,'flag':True,
               'label': 'Update Tax Structure', 'operation': 'update','new_tax_id':tax_details.tax_id}

    if not tax_structures:
        messages.info(request, 'Records not found')
        return render(request, 'billing/tax_structure.html', context=context)
    else:
        return render(request, 'billing/tax_structure.html', context=context)

    # except template.TemplateDoesNotExist:
    #     return render(request, 'billing/page-404.html')
    # except:
    #     return render(request, 'billing/page-500.html')


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
