# factories.py
import random
import string
from decimal import Decimal

import factory
from factory.django import DjangoModelFactory
from apps.home.models import Manufacturer, Product, ProductGroup, Customer
import faker

# fake = faker.Faker

def get_random_string():
    random_choices = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    return random_choices

def get_random_manufacturer():
    manufacturer = Manufacturer.objects.values_list('name')[:50]
    random_manufacturer = random.choice(manufacturer)
    return random_manufacturer

def get_random_number():
    number = random.randrange(100,10000)
    return number
# faker.

class ManufacturerFactory(DjangoModelFactory):
    class Meta:
        model = Manufacturer

    name = factory.Sequence(
        lambda n: f'manufacturer_{get_random_string()}_{n}'
    )
    sh_name = factory.Faker('company_suffix')
    type = factory.Faker('random_element', elements=['manufacturer', 'supplier'])
    address = factory.Faker('address')
    email = factory.Faker('email')
    contact = factory.Faker('basic_phone_number')



class GroupFactory(DjangoModelFactory):
    class Meta:
        model = ProductGroup


    group_id = factory.Sequence(
        lambda n: int(f'{get_random_number()}{n}')
    )
    group_name = factory.Sequence(
        lambda n: f'groupName_{get_random_string()}_{n}'
    )
    sh_name = factory.Faker('company_suffix')



class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product


    product_name = factory.Sequence(
        lambda n: f'products_{get_random_string()}_{n}'
    )
    product_code = factory.Sequence(
        lambda n: f'code_{get_random_string()}_{n}'
    )
    manufacturer = factory.SubFactory(ManufacturerFactory)
    buy_rate = factory.LazyAttribute(lambda _: round(random.uniform(100, 10000), 2))
    sell_rate = factory.LazyAttribute(
        lambda o: Decimal(o.buy_rate) + Decimal(random.randint(100, 1000))
    )
    mrp = factory.LazyAttribute(lambda o: o.sell_rate)
    contact = factory.Faker('basic_phone_number')
    group = factory.SubFactory(GroupFactory)


class CustomerFactory(DjangoModelFactory):
    class Meta:
        model = Customer


    customer_name = factory.Sequence(
        lambda n: f'customer_{get_random_string()}_{n}'
    )
    sh_name = factory.Sequence(
        lambda n: f'shName_{get_random_string()}_{n}'
    )
    contact = factory.Faker('basic_phone_number')
    address = factory.Faker('address')
    email = factory.Faker('email')
