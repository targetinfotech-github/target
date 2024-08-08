# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.billing import views
from apps.billing.views import login_view, register_user, Logout

urlpatterns = [

    # The billing page
    path('', views.index, name='billing'),


    # authentication
    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    path("logout/", Logout, name="logout"),


    # Manufacturers
    path('create_manufacturer/', views.create_manufacturer, name="create_manufacturer"),
    path('update_manufacturer/<int:pk>', views.update_manufacturer, name="update_manufacturer"),
    path('get_manufacturer_modal/', views.get_manufacturer_modal, name="get_manufacturer_modal"),
    path('delete_manufacturer/', views.delete_manufacturer, name="delete_manufacturer"),
    path('view_manufacturer/', views.view_manufacturer, name="view_manufacturer"),

    # Products
    path('create_product/', views.create_product, name="create_product"),
    path('get_product_modal/', views.get_product_modal, name="get_product_modal"),
    path('update_product/<int:pk>', views.update_product, name="update_product"),
    path('delete_product/', views.delete_product, name="delete_product"),
    path('view_product/', views.view_product, name="view_product"),

    # Receipts
    path('get_receipt_modal/', views.get_receipt_modal, name="get_receipt_modal"),
    path('add_product/<int:pk>', views.create_receipt, name="add_product"),

    # Groups
    path('create_group/', views.create_group, name="create_group"),
    path('view_group/', views.view_group, name="view_group"),
    path('get_group_modal/', views.get_group_modal, name="get_group_modal"),
    path('update_group/<int:pk>', views.update_group, name="update_group"),
    path('delete_group/', views.delete_group, name="delete_group"),

    # customer
    path('create_customer/', views.create_customer, name="create_customer"),
    path('get_customer_modal/', views.get_customer_modal, name="get_customer_modal"),
    path('view_customer/', views.view_customer, name="view_customer"),
    path('update_customer/<int:pk>', views.update_customer, name="update_customer"),
    path('delete_customer/', views.delete_customer, name="delete_customer"),
    path('search_router/<str:model_search>', views.search_router, name="search_router"),

    # tax Structure
    path('setup_tax_structure/', views.setup_tax_structure, name="setup_tax_structure"),

    # Selection List
    # sales rep
    path('setup_sales_rep/', views.setup_sales_rep, name="setup_sales_rep"),
    path('view_sales_rep/', views.view_sales_rep, name="view_sales_rep"),
    path('update_sales_rep/<int:pk>', views.update_sales_rep, name="update_sales_rep"),
    path('get_sales_rep_modal/', views.get_sales_rep_modal, name="get_sales_rep_modal"),
    path('delete_sales_rep/', views.delete_sales_rep, name="delete_sales_rep"),


    # Area
    path('setup_area/', views.setup_area, name="setup_area"),
    path('view_area/', views.view_area, name="view_area"),
    path('get_area_modal/', views.get_area_modal, name="get_area_modal"),
    path('update_area/<int:pk>', views.update_area, name="update_area"),
    path('delete_area/', views.delete_area, name="delete_area"),

    # manufacturer area
    path('setup_manufacturer_area/', views.setup_manufacturer_area, name="setup_manufacturer_area"),

    #manufacturer Representative
    path('setup_manufacturer_rep/', views.setup_manufacturer_rep, name="setup_manufacturer_rep"),

    #carriers
    path('setup_carriers/', views.setup_carriers, name="setup_carriers"),
    path('view_carriers/', views.view_carriers, name="view_carriers"),
    path('update_carriers/<int:pk>', views.update_carriers, name="update_carriers"),
    path('delete_carriers/', views.delete_carriers, name="delete_carriers"),
    path('get_carriers_modal/', views.get_carriers_modal, name="get_carriers_modal"),

    # units
    path('setup_units/', views.setup_units, name="setup_units"),
    path('view_units/', views.view_units, name="view_units"),
    path('update_units/<int:pk>', views.update_units, name="update_units"),
    path('delete_units/', views.delete_units, name="delete_units"),
    path('get_units_modal/', views.get_units_modal, name="get_units_modal"),

    #departments
    path('setup_departments/', views.setup_departments, name="setup_departments"),
    path('view_departments/', views.view_departments, name="view_departments"),
    path('update_departments/<int:pk>', views.update_departments, name="update_departments"),
    path('delete_departments/<int:pk>', views.delete_departments, name="delete_departments"),
    path('get_departments_modal/', views.get_departments_modal, name="get_departments_modal"),

    #division
    path('setup_division/', views.setup_division, name="setup_division"),
    path('view_division/', views.view_division, name="view_division"),
    path('update_division/<int:pk>', views.update_division, name="update_division"),
    path('delete_division/', views.delete_division, name="delete_division"),
    path('get_division_modal/', views.get_division_modal, name="get_division_modal"),

    # discount
    path('setup_discount_class/', views.setup_discount_class, name="setup_discount_class"),
    path('view_discount_class/', views.view_discount_class, name="view_discount_class"),
    path('update_discount_class/<int:pk>', views.update_discount_class, name="update_discount_class"),
    path('delete_discount_class/', views.delete_discount_class, name="delete_discount_class"),
    path('get_discount_class_modal/', views.get_discount_class_modal, name="get_discount_class_modal"),

    #customer class
    path('setup_customer_class/', views.setup_customer_class, name="setup_customer_class"),
    path('view_customer_class/', views.view_customer_class, name="view_customer_class"),
    path('update_customer_class/<int:pk>', views.update_customer_class, name="update_customer_class"),
    path('delete_customer_class/', views.delete_customer_class, name="delete_customer_class"),
    path('get_customer_class_modal/', views.get_customer_class_modal, name="get_customer_class_modal"),

    # UOM
    path('setup_uom/', views.setup_uom, name="setup_uom"),
    path('view_uom/', views.view_uom, name="view_uom"),
    path('update_uom/<int:pk>', views.update_uom, name="update_uom"),
    path('delete_uom/', views.delete_uom, name="delete_uom"),
    path('get_uom_modal/', views.get_uom_modal, name="get_uom_modal"),

    # brand name
    path('setup_brand_name/', views.setup_brand_name, name="setup_brand_name"),
    path('view_brand_name/', views.view_brand_name, name="view_brand_name"),
    path('update_brand_name/<int:pk>', views.update_brand_name, name="update_brand_name"),
    path('delete_brand_name/', views.delete_brand_name, name="delete_brand_name"),
    path('get_brand_name_modal/', views.get_brand_name_modal, name="get_brand_name_modal"),

    # payment method
    path('setup_payment_method/', views.setup_payment_method, name="setup_payment_method"),
    path('view_payment_method/<str:chosen_method>', views.view_payment_method, name="view_payment_method"),
    path('update_payment_method/<int:pk>', views.update_payment_method, name="update_payment_method"),
    path('delete_brand_name/', views.delete_payment_method, name="delete_payment_method"),
    path('get_payment_method_modal/', views.get_payment_method_modal, name="get_payment_method_modal"),
    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
