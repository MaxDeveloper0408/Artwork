from django.core.management.base import BaseCommand, CommandError
from settings.management.scripts import quote

class Command(BaseCommand):

    args = ''
    help = 'Export data to remote server'

    def handle(self, *args, **options):
        # Give the location of the file
        print('Importing Quotes')
        quote()
        print('Imported.')

