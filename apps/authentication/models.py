# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
from django.contrib.contenttypes.models import ContentType
class CustomUser(AbstractUser):
    class Meta:
        db_table = 'CustomUser'