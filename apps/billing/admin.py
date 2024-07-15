# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Manufacturer,Product

admin.site.register(Manufacturer)
admin.site.register(Product)