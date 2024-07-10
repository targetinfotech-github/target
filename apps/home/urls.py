# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),

    # Manufacturers
    path('create_manufacturer/',views.create_manufacturer, name="create_manufacturer"),
    path('update_manufacturer/<int:pk>',views.update_manufacturer, name="update_manufacturer"),
    path('get_manufacturer_modal/',views.get_manufacturer_modal, name="get_manufacturer_modal"),
    path('delete_manufacturer/<int:pk>',views.delete_manufacturer, name="delete_manufacturer"),
    path('view_manufacturer/',views.view_manufacturer, name="view_manufacturer"),

    # Products
    path('create_product/',views.create_product, name="create_product"),
    path('get_product_modal/',views.get_product_modal, name="get_product_modal"),
    path('update_product/<int:pk>',views.update_product, name="update_product"),
    path('delete_product/<int:pk>',views.delete_product, name="delete_product"),
    path('view_product/',views.view_product, name="view_product"),

    # Receipts
    path('get_receipt_modal/',views.get_receipt_modal, name="get_receipt_modal"),
    path('add_product/<int:pk>', views.create_receipt, name="add_product"),

    # Groups
    path('create_group/',views.create_group, name="create_group"),
    path('view_group/',views.view_group, name="view_group"),
    path('get_group_modal/',views.get_group_modal, name="get_group_modal"),
    path('update_group/<int:pk>',views.update_group, name="update_group"),
    path('delete_group/<int:pk>',views.delete_group, name="delete_group"),

    # customer
    path('create_customer/',views.create_customer, name="create_customer"),
    path('get_customer_modal/',views.get_customer_modal, name="get_customer_modal"),
    path('view_customer/',views.view_customer, name="view_customer"),
    path('update_customer/<int:pk>',views.update_customer, name="update_customer"),
    path('delete_customer/<int:pk>',views.delete_customer, name="delete_customer"),
    path('search_router/<str:model_search>',views.search_router, name="search_router"),
    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),
    

]
