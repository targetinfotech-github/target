# populate_manufacturers.py
from django.core.management.base import BaseCommand
from apps.billing.services.factories import ManufacturerFactory, ProductFactory, GroupFactory, CustomerFactory


class Command(BaseCommand):
    help = 'Populate the database with manufacturers'

    def add_arguments(self, parser):
        # parser.add_argument('count', type=int, help='The number of model to create')
        # parser.add_argument('model', type=int, help='Represents Model')
        parser.add_argument('--opt1', type=int, default=42, help='First optional argument with default value')
        parser.add_argument('--opt2', type=str, choices=['prod', 'group','cust','manu'],
                            help='Second optional argument with choices')

    def handle(self, *args, **kwargs):
        count = kwargs.get('opt1')
        model = kwargs.get('opt2')

        if model == 'prod':
            for _ in range(count):
                ProductFactory.create()
        elif model == 'group':
            for _ in range(count):
                GroupFactory.create()
        elif model == 'cust':
            for _ in range(count):
                CustomerFactory.create()
        elif model == 'manu':
            for _ in range(count):
                ManufacturerFactory.create()
        self.stdout.write(f'Positional argument 1: {count}')
        self.stdout.write(f'Positional argument 2: {model}')
        if count is not None:
            self.stdout.write(f'Optional argument 1: {count}')
        if model is not None:
            self.stdout.write(f'Optional argument 2: {model}')
