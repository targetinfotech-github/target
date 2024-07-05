# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django.db.models import Count
from django.test import TestCase, TransactionTestCase

# Create your tests here.
# from django.tests import TestCase
from django.urls import reverse
from apps.home.form import ManufacturerForm
from django.utils.crypto import get_random_string
from unittest import TestCase
from apps.home.models import Manufacturer
import random
import string

# class MyViewTest(TestCase):
#     def test_get_view(self):
#         response = self.client.get(reverse('view_group'))
#         print(response)
#         self.assertEqual(response.status_code,200)


class TestCreateManufacturer(TestCase):
    def generate_random_string(self,length):
        alphabets = string.ascii_letters+string.digits
        random_string = ''.join(random.choice(alphabets) for _ in range(length))
        return random_string

    def test_form_data(self):
        TYPE_CHOICES = [
            ('manufacturer', 'Manufacturer'),
            ('supplier', 'Supplier'),
        ]
        for i in range(10):
            name = f'Manufacturer {i+1}'
            print(name)
            type_choice = random.choice(TYPE_CHOICES)[0]
            data = {
                'name': name,
                'type':type_choice,
                'sh_name': self.generate_random_string(10),
                'address': self.generate_random_string(200),
                'email': self.generate_random_string(8) + '@gmail.com',
                'contact': self.generate_random_string(10)
            }
            # print(data)
            form = ManufacturerForm(data)
            self.assertTrue(form.is_valid(), msg=form.errors)
            response = self.client.post(reverse('create_manufacturer'), data=data)
            manufacturer = Manufacturer.objects.all().count()
            print(manufacturer)
        # self.assertEqual(response.status_code, 302)
        # self.assertRedirects(response, reverse('home'))

        # Verify the manufacturer was created
        # self.assertTrue(Manufacturer.objects.filter(name=name).exists())
#
class TestViewManufacturer(TestCase):
    def test_create_manufacturer(self):
        print('-----------')
        manufacturer = Manufacturer.objects.all()
        print(manufacturer)
