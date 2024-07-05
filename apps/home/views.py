# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import json
import time

from django import template
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.views.generic import ListView

from apps.home.decorators import measure_execution_time
from apps.home.form import ManufacturerForm, ProductForm, ReceiptForm, GroupForm, CustomerForm
from django.shortcuts import render,redirect,get_list_or_404,get_object_or_404
from apps.home.models import Manufacturer, Product, Receipt, ReceiptProduct, Group, Customer
from django.core.serializers import serialize
import json

# views.py or any module

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

# @login_required(login_url="/login/")
@measure_execution_time
def index(request):
    context = {'segment': 'index'}
    manufacturer = Manufacturer.objects.count()
    group = Group.objects.count()
    product = Product.objects.count()
    customer = Customer.objects.count()
    print(group)
    print(manufacturer)
    print(product)
    print(customer)
    html_template = loader.get_template('home/dashboard.html')
    return HttpResponse(html_template.render(context, request))


# @login_required(login_url="/login/")
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
    
# @login_required(login_url="/login/")
@measure_execution_time
def create_manufacturer(request):
    try:
        manufacturer = Manufacturer.objects.all()
        print(manufacturer)
        if request.method == 'POST':
            print('post data')
            form = ManufacturerForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data['name']
                print(f'form name:: {name}')
                form.save()
                print('form saved')
                man = Manufacturer.objects.get(name = name)
                print(f'man:: {man.type}')
                return HttpResponseRedirect(reverse('home'))
        else:
            form = ManufacturerForm()
        context = {'form':form,
                   'product_data':None,
                   'flag':'create',
                   'label':'Create Manufacturer'}
        return render(request, 'home/manufacturer.html', context)
    except template.TemplateDoesNotExist:
        return render(request, 'home/page-404.html')
    except:
        return render(request, 'home/page-500.html')


# @login_required(login_url="/login/")
@measure_execution_time
def get_manufacturer_modal(request):
    # try:
    manufacturer_data = Manufacturer.objects.annotate(
        product_count=Count('product_manufacturer')).values(
        'id', 'name', 'type', 'sh_name', 'print_name', 'product_count'
    )
    # manufacturer_data = Manufacturer.objects.values('id','name','contact', 'sh_name','print_name')
    form = ManufacturerForm()
    context = {'manufacturer_data':manufacturer_data,'form':form, 'flag':'modal',
               'label':'Update Manufacturer'}
    if request.method == 'POST':
        if 'submit_selected_record' in request.POST:
            id = request.POST['submit_selected_record']
            return redirect('update_manufacturer',int(id))
        elif 'delete_selected_record' in request.POST:
            id = request.POST['delete_selected_record']
            return redirect('delete_manufacturer', int(id))
        else:
            return redirect('create_manufacturer')
    return render(request, 'home/manufacturer.html', context=context)
    # except template.TemplateDoesNotExist:
    #     return render(request,'home/page-404.html')
    # except:
    #     return render(request,'home/page-500.html')

# @login_required(login_url="/login/")
@measure_execution_time
def update_manufacturer(request,pk):
    try:
        manufacturer_data = Manufacturer.objects.get(id=pk)
        print(manufacturer_data)
        if request.method == 'POST':
            form = ManufacturerForm(request.POST, instance=manufacturer_data)
            if form.is_valid():
                form.save()
                return redirect('home')
        else:
            form = ManufacturerForm(instance=manufacturer_data)
        context = {'form':form,'manufacturer_data':None,'flag':'update',
                   'label':'Update Manufacturer'}
        return render(request, 'home/manufacturer.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request,'home/page-404.html')
    except:
        return render(request,'home/page-500.html')


# @login_required(login_url="/login/")
@measure_execution_time
def delete_manufacturer(request,pk):
    try:
        manufacturer = Manufacturer.objects.get(id=pk)
        manufacturer.delete()
        return redirect('home')
    except template.TemplateDoesNotExist:
        return render(request, 'home/page-404.html')
    except:
        return render(request, 'home/page-500.html')

# @login_required(login_url="/login/")
@measure_execution_time
def view_manufacturer(request):
    try:
        if request.method == 'POST':
            manufacturer_name = request.POST.get('manufacturer_name')
            if manufacturer_name:
                manufacturer_data = Manufacturer.objects.filter(name__icontains=manufacturer_name)
            else:
                manufacturer_data = Manufacturer.objects.all()
        else:
            manufacturer_data = Manufacturer.objects.all()

        manufacturer_name = list(Manufacturer.objects.values_list('name', flat=True))
        dataJson = json.dumps(manufacturer_name)
        context = {'flag':'view','manufacturer_data':manufacturer_data,
               'dataJson': dataJson,'label':'View Manufacturer'}
        return render(request, 'home/manufacturer.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request,'home/page-404.html')
    except:
        return render(request,'home/page-500.html')


# @login_required(login_url="/login/")
@measure_execution_time
def create_product(request):
    try:
        start_time = time.time()
        Group.objects.get_or_create_general_manufacturer()
        group_time = time.time() - start_time
        print(f'Group time: {group_time}')
        if request.method == 'POST':
            form = ProductForm(request.POST)
            print('post')
            if form.is_valid():
                print('form valid')
                form.save()
                print(Product.objects.values())
                return HttpResponseRedirect(reverse('home'))
        else:
            start = time.time()
            form = ProductForm()
            print(f'form time: {time.time() - start}')
        context = {'form': form,
                   'manufacturer_data': None,
                   'flag': 'create',
                   'label':'Create Product'}
        return render(request, 'home/products.html', context)
    except template.TemplateDoesNotExist:
        return render(request,'home/page-404.html')
    except:
        return render(request,'home/page-500.html')


# @login_required(login_url="/login/")
@measure_execution_time
def get_product_modal(request):
    try:
        # product_data = Product.objects.values('id','product_name','product_code',
        #                                      'manufacturer','buy_rate','sell_rate')
        product_data = Product.objects.select_related('manufacturer').\
        values('id', 'product_name', 'product_code',
               'manufacturer__name', 'buy_rate', 'sell_rate')
        # product_name = Product.objects.values('product_name')
        form = ProductForm()
        context = {'product_data': product_data, 'form': form, 'flag': 'modal',
                   'label':'Update Product'}
        if request.method == 'POST':
            if 'submit_selected_record' in request.POST:
                id = request.POST['submit_selected_record']
                return redirect('update_product', int(id))
            elif 'delete_selected_record' in request.POST:
                id = request.POST['delete_selected_record']
                return redirect('delete_product', int(id))
            else:
                return redirect('create_product')
        return render(request, 'home/products.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request, 'home/page-404.html')
    except:
        return render(request, 'home/page-500.html')


# @login_required(login_url="/login/")
@measure_execution_time
def delete_product(request,pk):
    try:
        product = Product.objects.get(id=pk)
        product.delete()
        return redirect('home')
    except template.TemplateDoesNotExist:
        return render(request,'home/page-404.html')
    except:
        return render(request,'home/page-500.html')


# @login_required(login_url="/login/")
@measure_execution_time
def update_product(request,pk):
    try:
        product_data = Product.objects.get(id=pk)
        if request.method == 'POST':
            form = ProductForm(request.POST, instance=product_data)
            if form.is_valid():
                form.save()
                return redirect('home')
        else:
            form = ProductForm(instance=product_data)
        context = {'form': form, 'product_data': None, 'flag': 'update','label':'Update Product'}
        return render(request, 'home/products.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request,'home/page-404.html')
    except:
        return render(request,'home/page-500.html')

# @login_required(login_url="/login/")
@measure_execution_time
def view_product(request):
    try:
        if request.method == 'POST':
            product_name = request.POST.get('product_name')
            if product_name:
                product_data = Product.objects.filter(product_name=product_name)
            else:
                product_data = Product.objects.all()
        else:
            start = time.time()
            product_data = Product.objects.all()
            end = time.time()
            print(f'total time for product.all()::{end-start}')
        start = time.time()
        product_name = list(Product.objects.values_list('product_name', flat=True))
        end = time.time()
        print(f'total time for product_name::{end - start}')
        dataJson = json.dumps(product_name)
        context = {'flag': 'view', 'product_data': product_data,'dataJson':dataJson,
                   'label':'View Product'}
        return render(request, 'home/products.html', context)
    except template.TemplateDoesNotExist:
        return render(request,'home/page-404.html')
    except:
        return render(request,'home/page-500.html')

# @login_required(login_url="/login/")
@measure_execution_time
def get_receipt_modal(request):
    try:
        if request.method == 'POST':
            form = ReceiptForm(request.POST)
            if form.is_valid():
                print('get receipt model submitted')
                receipt = form.save()
                id = receipt.id
                return redirect('add_product',pk=id)
        else:
            form = ReceiptForm()
        context = {'form': form, 'flag': 'modal'}
        return render(request, 'home/receipt.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request,'home/page-404.html')
    except Exception as e:
        print(e)
        return render(request,'home/page-500.html')

# @login_required(login_url="/login/")
@measure_execution_time
def add_product(request,pk):
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
            reset = request.POST.get('reset',None)
            submit = request.POST.get('submit',None)
            if reset is not None:
                receipt.delete()
                return redirect('home')
                # create a html file to display record deleted successfully
            elif submit is not None:
                product_inputs = []
                net_amount = request.POST.get('net_amount_input','')
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
                    print(f'receipt_product:{receipt_product.product.product_name}, quantity:{receipt_product.quantity}, discount:{receipt_product.discount}')
                else:
                    receipt.delete()
                return redirect('home')
        context = {'flag': 'product','product_data':product_data}
        return render(request, 'home/receipt.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request,'home/page-404.html')
    except Exception as e:
        print(e)
        return render(request,'home/page-500.html')


# @login_required(login_url="/login/")
@measure_execution_time
def create_group(request):
    # try:
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = GroupForm()
    context = {'form': form, 'flag': 'create','label':'Create Group'}
    return render(request, 'home/group.html', context=context)
    # except template.TemplateDoesNotExist:
    #     return render(request,'home/page-404.html')
    # except:
    #     return render(request,'home/page-500.html')

# @login_required(login_url="/login/")
@measure_execution_time
def view_group(request):
    try:
        if request.method == 'POST':
            group_name = request.POST.get('group_name')
            print(group_name)
            if group_name:
                group_data = Group.objects.filter(group_name=group_name)
            else:
                group_data = Group.objects.all()
        else:
            group_data = Group.objects.all()
        group_name = list(Group.objects.values_list('group_name', flat=True))
        dataJson = json.dumps(group_name)
        context = {'flag': 'view', 'group_data': group_data,'dataJson':dataJson,'label':'View Group'}
        return render(request, 'home/group.html', context)
    except template.TemplateDoesNotExist:
        return render(request,'home/page-404.html')
    except:
        return render(request,'home/page-500.html')

@measure_execution_time
def get_group_modal(request):
    # try:
    group_data = Group.objects.exclude(group_name='General Manufacturer').annotate(
        product_count = Count('product_group')
    ).values('id', 'group_id', 'group_name',
            'print_name', 'sh_name', 'hsn_code','product_count')
    general_manufacturer = Group.objects.filter(group_name='General Manufacturer').annotate(
        product_count = Count('product_group')).values('id', 'group_id', 'group_name',
        'print_name', 'sh_name', 'hsn_code','product_count')
    print(group_data)
    print(general_manufacturer)
    form = GroupForm()
    if request.method == 'POST':
        if 'submit_selected_record' in request.POST:
            id = request.POST['submit_selected_record']
            return redirect('update_group', int(id))
        elif 'delete_selected_record' in request.POST:
            id = request.POST['delete_selected_record']
            return redirect('delete_group', int(id))
        else:
            return redirect('create_group')
    # removable = False if Group.objects.prefetch_related('product_group').exists() else True
    context = {'form': form, 'flag': 'modal','label': 'Update Group',
               'group_data':group_data,'label':'Update Group','general_manufacturer':general_manufacturer}
    return render(request, 'home/group.html', context=context)
    # except template.TemplateDoesNotExist:
    #     return render(request,'home/page-404.html')
    # except Exception as e:
    #     print(e)
    #     return render(request,'home/page-500.html')



# @login_required(login_url="/login/")
@measure_execution_time
def update_group(request,pk):
    try:
        group_data = Group.objects.get(id=pk)
        if request.method == 'POST':
            form = GroupForm(request.POST, instance=group_data)
            if form.is_valid():
                form.save()
                return redirect('home')
        else:
            form = GroupForm(instance=group_data)
        context = {'form': form, 'flag': 'update', 'label': 'Update Group',
                   'group_data': None}
        return render(request, 'home/group.html', context=context)
    except template.TemplateDoesNotExist:
        return render(request,'home/page-404.html')
    except:
        return render(request,'home/page-500.html')


# @login_required(login_url="/login/")
@measure_execution_time
def delete_group(request,pk):
    # try:
    group = Group.objects.get(id=pk)
    if group.product_group.exists():
        print('product under group exists')
    else:
        group.delete()
    return redirect('home')
    # except template.TemplateDoesNotExist:
    #     return render(request, 'home/page-404.html')
    # except:
    #     return render(request, 'home/page-500.html')



# @login_required(login_url="/login/")
@measure_execution_time
def create_customer(request):
    # try:
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('home'))
    else:
        form = CustomerForm()
    context = {'form':form,
               'customer_data':None,
               'flag':'create',
               'label':'Create Customer'}
    return render(request, 'home/customer.html', context)
    # except template.TemplateDoesNotExist:
    #     return render(request, 'home/page-404.html')
    # except:
    #     return render(request, 'home/page-500.html')


# @login_required(login_url="/login/")
@measure_execution_time
def get_customer_modal(request):
    # try:
    customer_data = Customer.objects.values('id','customer_name',
    'sh_name','print_name')
    # manufacturer_data = Manufacturer.objects.values('id','name','contact', 'sh_name','print_name')
    form = CustomerForm()
    context = {'customer_data':customer_data,'form':form, 'flag':'modal',
               'label':'Update Customer'}
    if request.method == 'POST':
        if 'submit_selected_record' in request.POST:
            id = request.POST['submit_selected_record']
            print(id)
            return redirect('update_customer',int(id))
        elif 'delete_selected_record' in request.POST:
            id = request.POST['delete_selected_record']
            return redirect('delete_customer', int(id))
        else:
            return redirect('create_customer')
    return render(request, 'home/customer.html', context=context)
    # except template.TemplateDoesNotExist:
    #     return render(request,'home/page-404.html')
    # except:
    #     return render(request,'home/page-500.html')

# @login_required(login_url="/login/")/
@measure_execution_time
def update_customer(request,pk):
    # try:
    customer_data = Customer.objects.get(id=pk)
    print(customer_data)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer_data)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = CustomerForm(instance=customer_data)
    context = {'form':form,'customer_data':customer_data,'flag':'update',
               'label':'Update Customer'}
    return render(request, 'home/customer.html', context=context)
    # except template.TemplateDoesNotExist:
    #     return render(request,'home/page-404.html')
    # except:
    #     return render(request,'home/page-500.html')


# @login_required(login_url="/login/")
@measure_execution_time
def delete_customer(request,pk):
    try:
        customer = Customer.objects.get(id=pk)
        customer.delete()
        return redirect('home')
    except template.TemplateDoesNotExist:
        return render(request, 'home/page-404.html')
    except:
        return render(request, 'home/page-500.html')

# @login_required(login_url="/login/")
@measure_execution_time
def view_customer(request):
    # try:
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        if customer_name:
            customer_data = Customer.objects.filter(name__icontains=customer_name)
        else:
            customer_data = Customer.objects.all()
    else:
        customer_data = Customer.objects.all()

    customer_name = list(Customer.objects.values_list('customer_name', flat=True))
    dataJson = json.dumps(customer_name)
    context = {'flag':'view','customer_data':customer_data,
           'dataJson': dataJson,'label':'View Customer'}
    return render(request, 'home/customer.html', context=context)
    # except template.TemplateDoesNotExist:
    #     return render(request,'home/page-404.html')
    # except:
    #     return render(request,'home/page-500.html')
