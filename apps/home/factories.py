# factories.py
import random
from decimal import Decimal

import factory
from factory.django import DjangoModelFactory
from apps.home.models import Manufacturer, Product, Group
import faker

faker = faker.Faker


# faker.
class ManufacturerFactory(DjangoModelFactory):
    class Meta:
        model = Manufacturer

    name = factory.Faker('company')
    sh_name = factory.Faker('company_suffix')
    type = factory.Faker('random_element', elements=['manufacturer', 'supplier'])
    address = factory.Faker('address')
    email = factory.Faker('email')
    contact = factory.Faker('basic_phone_number')

class GroupFactory(DjangoModelFactory):
    class Meta:
        model = Group

class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product
    # faker.
    rate = random.randrange(100, 1000)
    product_name = factory.Faker('canton_name')
    product_code = factory.Faker('org_id')
    manufacturer = factory.SubFactory(ManufacturerFactory)
    type = factory.Faker('random_element', elements=['manufacturer', 'supplier'])
    address = factory.Faker('address')

    buy_rate = factory.Faker('decimal', max_digits=8, decimal_places=2, min_value=100.00)
    rate = factory.LazyAttribute(lambda o: random.randrange(100, 1000))  # Generate a random integer between 100 and 1000
    sell_rate = factory.LazyAttribute(
        lambda o: Decimal(o.buy_rate) + Decimal(o.rate))  # sell_rate is buy_rate plus rate
    mrp = factory.LazyAttribute(lambda o: o.sell_rate)  # Ensure `
    contact = factory.Faker('basic_phone_number')
    group = factory.SubFactory(GroupFactory)