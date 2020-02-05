from django.core.management.base import BaseCommand, CommandError
from arts.models import Order,Product
from datetime import datetime,timedelta
from Aartcy.utils.extras import get_time,transferred_amount,chartify
import random
class Command(BaseCommand):
    args = ''
    help = 'Export data to remote server'

    def handle(self, *args, **options):
        # product = Product.objects.get(id=65)
        # Order.objects.filter(email='shani@gmail.com').update(product=product)

        orders = Order.objects.all()
        for i,order in enumerate(orders,start=1):
            order.address = 'sample'
            order.save()
            print(i,'orders updated.')

