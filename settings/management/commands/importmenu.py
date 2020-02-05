from django.core.management.base import BaseCommand, CommandError
from settings.management.scripts import menu_items
from settings.management.scripts import import_stripe_settings

class Command(BaseCommand):

    args = ''
    help = 'Export data to remote server'

    def handle(self, *args, **options):
        # Give the location of the file
        print('Importing Menu')
        menu_items()
        print('Imported.')

