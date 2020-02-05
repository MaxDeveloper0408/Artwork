from django.core.management.base import BaseCommand, CommandError
from settings.management.scripts import *
class Command(BaseCommand):

    args = ''
    help = 'Export data to remote server'

    def handle(self, *args, **options):

        print('Importing Menu')
        menu_items()
        print('Menu Imported.')
        print('Importing Stripe Settings')
        import_stripe_settings()
        print('Stripe Settings Imported')
        print('Importing Quotes')
        quote()
        print('Imported.')

