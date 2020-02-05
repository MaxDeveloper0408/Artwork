from django.core.management.base import BaseCommand, CommandError
from arts.models import Order
from datetime import datetime,timedelta
from Aartcy.utils.extras import get_time,transferred_amount,chartify

class Command(BaseCommand):
    args = ''
    help = 'Export data to remote server'

    def handle(self, *args, **options):
        # Give the location of the file
        tags = ['Test','Sample','sample','test','corgy','love dogs','  corgy']
        date = get_time('Y').date()
        current_date = datetime.today().date()
        while date <= current_date:
            print(date)
            o =Order.objects.filter(created_at=date)
            o.delete()
            date = date + timedelta(days=1)
        # Order.objects.all().delete()


