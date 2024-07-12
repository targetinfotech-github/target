# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import time

from django import template
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.urls import reverse

from apps.home.services.decorators import measure_execution_time
from apps.home.form import ManufacturerForm, ProductForm, ReceiptForm, GroupForm, CustomerForm
from django.shortcuts import render, redirect
from apps.home.models import Manufacturer, Product, Receipt, ReceiptProduct, ProductGroup, Customer
import json

# views.py or any module

import logging

from apps.home.services.resource_manager import SetupContext
from apps.home.services.search_manager import SearchService, masterSearchEndpoint

# Get an instance of a logger
logger = logging.getLogger(__name__)


@measure_execution_time
@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}
    manufacturer = Manufacturer.objects.count()
    group = ProductGroup.objects.count()
    product = Product.objects.count()
    customer = Customer.objects.count()
    print(group)
    print(manufacturer)
    print(product)
    print(customer)
    html_template = loader.get_template('home/dashboard.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
@measure_execution_time
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        load_template = request.path.split('/')[-1]
        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template
        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        return render(request, 'home/page-404.html')
    except:
        return render(request, 'home/page-500.html')


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



@login_required(login_url="/login/")
@measure_execution_time
def create_manufacturer(request):
    # try:
    if request.method == 'POST':
        form = ManufacturerForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            form.save()
            messages.success(request, f'Manufacturer {name} created')
            return redirect('create_manufacturer')

    form = ManufacturerForm()
    context_obj = SetupContext(model_search='manufacturer', operation='create')
    context = context_obj.get_context()
    context['form'] = form


    return render(request, 'home/manufacturer.html', context)
    # except template.TemplateDoesNotExist:
    #     return render(request, 'home/page-404.html')
    # except:
    #     return render(request, 'home/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def get_manufacturer_modal(request):
    # try:
    query = ''
    manufacturer_data = Manufacturer.objects.annotate(
        product_count=Count('product_manufacturer')
    ).values(
        'id', 'name', 'type', 'sh_name', 'print_name', 'product_count'
    ).order_by('name')

    if request.method == 'POST':
        if 'submit_selected_record' in request.POST:
            id = request.POST['submit_selected_record']
            return redirect('update_manufacturer', int(id))
        elif 'delete_selected_record' in request.POST:
            id = request.POST['delete_selected_record']
            return redirect('delete_manufacturer', int(id))
        else:
            return redirect('create_manufacturer')
    page_obj = pagination(request, manufacturer_data)
    context_obj = SetupContext(model_search='manufacturer_model', page_obj=page_obj,operation='modal')
    context = context_obj.get_context()

    return render(request, 'home/manufacturer.html', context=context)
    # except template.TemplateDoesNotExist:
    #     return render(request,'home/page-404.html')
    # except:
    #     return render(request,'home/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def update_manufacturer(request, pk):
    try:
        manufacturer_data = Manufacturer.objects.get(id=pk)
        if request.method == 'POST':
            form = ManufacturerForm(request.POST, instance=manufacturer_data)
            if form.is_valid():
                name = form.cleaned_data['name']
                form.save()
                messages.success(request, f'Manufacturer {name} created')
                return redirect('update_manufacturer')
        else:
            form = ManufacturerForm(instance=manufacturer_data)
        context_obj = SetupContext(model_search='manufacturer', operation='update')
        context = context_obj.get_context()
        context['form'] = form

        return render(request, 'home/manufacturer.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'home/page-404.html')
    except:
        return render(request, 'home/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def delete_manufacturer(request, pk):
    try:
        manufacturer = Manufacturer.objects.get(id=pk)
        manufacturer.delete()
        return redirect('home')
    except template.TemplateDoesNotExist:
        return render(request, 'home/page-404.html')
    except:
        return render(request, 'home/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def view_manufacturer(request):
    try:
        query = ''
        if request.method == 'POST':
            manufacturer_name = request.POST.get('manufacturer_name')
            if manufacturer_name:
                manufacturer_data = Manufacturer.objects.filter(name__icontains=manufacturer_name).\
                    values('id','name','print_name','sh_name','contact').order_by('name')
            else:
                manufacturer_data = Manufacturer.objects.all().values('id','name','print_name','sh_name','contact')\
                    .order_by('name')
        else:
            manufacturer_data = Manufacturer.objects.all().values('id','name','print_name','sh_name','contact')\
                .order_by('name')

        page_obj = pagination(request, manufacturer_data)
        context_obj = SetupContext(model_search='manufacturer',page_obj=page_obj, operation='view')
        context = context_obj.get_context()

        return render(request, 'home/manufacturer.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'home/page-404.html')
    except:
        return render(request, 'home/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def create_product(request):
    # try:
    ProductGroup.objects.get_or_create_general_manufacturer()
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['product_name']
            form.save()
            messages.success(request, f'Product {name} created')
            return redirect('create_product')
    else:
        form = ProductForm()
    context_obj = SetupContext(model_search='product', operation='create')
    context = context_obj.get_context()
    context['form'] = form
    return render(request, 'home/products.html', context)
    # except template.TemplateDoesNotExist:
    #     return render(request, 'home/page-404.html')
    # except:
    #     return render(request, 'home/page-500.html')


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
                return redirect('delete_product', int(id))
            else:
                return redirect('create_product')
        page_obj = pagination(request, product_data)
        context_obj = SetupContext(model_search='product_model', page_obj=page_obj, operation='modal')
        context = context_obj.get_context()
        return render(request, 'home/products.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'home/page-404.html')
    except:
        return render(request, 'home/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def delete_product(request, pk):
    try:
        product = Product.objects.get(id=pk)
        product.delete()
        return redirect('home')
    except template.TemplateDoesNotExist:
        return render(request, 'home/page-404.html')
    except:
        return render(request, 'home/page-500.html')


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
                return redirect('update_product')
        else:
            form = ProductForm(instance=product_data)
        context_obj = SetupContext(model_search='product', operation='update')
        context = context_obj.get_context()
        context['form'] = form
        return render(request, 'home/products.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'home/page-404.html')
    except:
        return render(request, 'home/page-500.html')


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

        return render(request, 'home/products.html', context)
    except template.TemplateDoesNotExist:
        return render(request, 'home/page-404.html')
    except:
        return render(request, 'home/page-500.html')


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
        return render(request, 'home/receipt.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'home/page-404.html')
    except Exception as e:
        print(e)
        return render(request, 'home/page-500.html')


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
            return redirect('home')
        product_data = Product.objects.filter(manufacturer=receipt.manufacturer)
        if request.method == 'POST':
            reset = request.POST.get('reset', None)
            submit = request.POST.get('submit', None)
            if reset is not None:
                receipt.delete()
                return redirect('home')
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
                return redirect('home')
        context = {'flag': 'product', 'product_data': product_data}
        return render(request, 'home/receipt.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'home/page-404.html')
    except Exception as e:
        print(e)
        return render(request, 'home/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def create_group(request):
    # try:
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['group_name']
            form.save()
            messages.success(request,f'Group {name} created')
            return redirect('create_group')
    else:
        form = GroupForm()
    context_obj = SetupContext(model_search='group', operation='create')
    context = context_obj.get_context()
    context['form'] = form
    return render(request, 'home/group.html', context=context)
    # except template.TemplateDoesNotExist:
    #     return render(request, 'home/page-404.html')
    # except:
    #     return render(request, 'home/page-500.html')


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
        return render(request, 'home/group.html', context)
    except template.TemplateDoesNotExist:
        return render(request, 'home/page-404.html')
    except:
        return render(request, 'home/page-500.html')


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
                return redirect('delete_group', int(id))
            else:
                return redirect('create_group')
        page_obj = pagination(request, group_data)
        context_obj = SetupContext(model_search='group', page_obj=page_obj, operation='modal')
        context = context_obj.get_context()
        return render(request, 'home/group.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'home/page-404.html')
    except Exception as e:
        print(e)
        return render(request, 'home/page-500.html')


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
                messages.success(request,f'Group {name} updated')
                return redirect('update_group')
        else:
            form = GroupForm(instance=group_data)
        context_obj = SetupContext(model_search='group', operation='update')
        context = context_obj.get_context()
        context['form'] = form
        return render(request, 'home/group.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'home/page-404.html')
    except:
        return render(request, 'home/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def delete_group(request, pk):
    try:
        group = ProductGroup.objects.get(id=pk)
        if group.product_group.exists():
            print('product under group exists')
        else:
            group.delete()
        return redirect('home')
    except template.TemplateDoesNotExist:
        return render(request, 'home/page-404.html')
    except:
        return render(request, 'home/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def create_customer(request):
    try:
        if request.method == 'POST':
            form = CustomerForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data['customer_name']
                form.save()
                messages.success(request, f'Customer {name} created')
                return redirect('create_customer')
        else:
            form = CustomerForm()
        context_obj = SetupContext(model_search='customer', operation='create')
        context = context_obj.get_context()
        context['form'] = form
        return render(request, 'home/customer.html', context)
    except template.TemplateDoesNotExist:
        return render(request, 'home/page-404.html')
    except:
        return render(request, 'home/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def get_customer_modal(request):
    try:
        customer_data = Customer.objects.values('id', 'customer_name',
                                                'sh_name', 'print_name','email').order_by('customer_name')
        if request.method == 'POST':
            if 'submit_selected_record' in request.POST:
                id = request.POST['submit_selected_record']
                print(id)
                return redirect('update_customer', int(id))
            elif 'delete_selected_record' in request.POST:
                id = request.POST['delete_selected_record']
                return redirect('delete_customer', int(id))
            else:
                return redirect('create_customer')
        paginator = Paginator(customer_data, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context_obj = SetupContext(model_search='customer',page_obj=page_obj, operation='modal')
        context = context_obj.get_context()
        return render(request, 'home/customer.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'home/page-404.html')
    except:
        return render(request, 'home/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def update_customer(request, pk):
    try:
        customer_data = Customer.objects.get(id=pk)
        if request.method == 'POST':
            form = CustomerForm(request.POST, instance=customer_data)
            if form.is_valid():
                name = form.cleaned_data['customer_name']
                form.save()
                messages.success(request, f'Customer {name} updated')
                return redirect('update_customer')
        else:
            form = CustomerForm(instance=customer_data)
        context_obj = SetupContext(model_search='customer', operation='update')
        context = context_obj.get_context()
        context['form'] = form
        return render(request, 'home/customer.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'home/page-404.html')
    except:
        return render(request, 'home/page-500.html')


@login_required(login_url="/login/")
@measure_execution_time
def delete_customer(request, pk):
    try:
        customer = Customer.objects.get(id=pk)
        customer.delete()
        return redirect('home')
    except template.TemplateDoesNotExist:
        return render(request, 'home/page-404.html')
    except:
        return render(request, 'home/page-500.html')


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

        context_obj = SetupContext(model_search='customer',page_obj=page_obj, operation='view')
        context = context_obj.get_context()
        return render(request, 'home/customer.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'home/page-404.html')
    except:
        return render(request, 'home/page-500.html')


@measure_execution_time
def search_router(request, model_search):
    autocomplete_query = request.GET.get('autocomplete_query', '')
    manufacturer_modal_details = request.GET.get('manufacturer_modal_details', '')
    print(f'manufacturer_modal_details ::{manufacturer_modal_details},, modal_search: {model_search}, request:{request}')
    masterSearchObject = masterSearchEndpoint(request, model_search)
    if autocomplete_query:
        json_object = masterSearchObject.autocomplete_data()
        return json_object
    else:
        template, context = masterSearchObject.masterSearchRouter()
        return render(request, template, context)
