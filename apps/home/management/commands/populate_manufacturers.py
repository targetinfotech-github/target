# populate_manufacturers.py
from django.core.management.base import BaseCommand
from apps.home.services.factories import ManufacturerFactory


class Command(BaseCommand):
    help = 'Populate the database with manufacturers'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='The number of manufacturers to create')

    def handle(self, *args, **kwargs):
        count = kwargs['count']
        for _ in range(count):
            ManufacturerFactory.create()
        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} manufacturers'))
