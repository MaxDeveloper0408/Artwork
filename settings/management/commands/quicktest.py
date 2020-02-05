from django.core.management.base import BaseCommand, CommandError
from arts.models import Tag,Order
from django.db import IntegrityError

class Command(BaseCommand):
    args = ''
    help = 'Export data to remote server'

    def handle(self, *args, **options):
        # Give the location of the file
        # tags = ['Test','Sample','sample','test','corgy','love dogs','  corgy']
        #
        # for t in tags:
        #     try:
        #         tag = Tag.objects.create(name=t)
        #     except IntegrityError as e:
        #         print(str(e))

        orders = Order.objects.complete().delete()
