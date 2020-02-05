from django.core.management.base import BaseCommand, CommandError
from arts.models import Order
from datetime import datetime,timedelta
from Aartcy.utils.extras import get_time,transferred_amount,chartify
import random
class Command(BaseCommand):
    args = ''
    help = 'Export data to remote server'

    def handle(self, *args, **options):
        # Give the location of the file
        tags = ['Test','Sample','sample','test','corgy','love dogs','  corgy']
        date = get_time('Y').date()
        original_date = get_time('Y').date()
        current_date = datetime.today().date()
        a = 0
        while date <= current_date:
            orders = [12768, 12587, 12767, 12766]
            any_order = Order.objects.get(id=random.choice(orders))
            o =Order.objects.create(email=any_order.email,
                                 product=any_order.product,
                                 status='C',
                                 data=any_order.data,
                                 price=any_order.price,
                                 address=any_order.price,
                                 by=any_order.by,
                                 created_at=date)
            o.save()
            o.created_at = date
            o.save()
            date = date + timedelta(days=1)

            if date == current_date:
                date = original_date
                a+=1
                print(a,'times')

