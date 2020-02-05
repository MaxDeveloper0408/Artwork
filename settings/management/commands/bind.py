import os
import shutil

from django.core.management.base import BaseCommand

from django.conf import settings

class Command(BaseCommand):
    """
        Binds angular with django.
    """
    args = ''
    help = 'Export data to remote server'

    def handle(self, *args, **options):

        ANGULAR = 'angular'
        ASSETS = 'assets'

        origin = settings.BASE_DIR + '/dist'
        destination = settings.BASE_DIR + '/static'
        folders = ['static'] #folders in dist.
        #Root Files
        files_path = {
                        origin+'/4.js':destination,
                        origin+'/5.js':destination,
                        origin+'/6.js':destination,
                        origin+'/7.js':destination,
                     }

        # destination paths
        folders_path = {origin+'/static/assets/':f'{destination}/{ASSETS}/',}
        root_files_destination = f'{destination}/{ANGULAR}/'

        try:
            shutil.rmtree(destination, ignore_errors=False, onerror=None)
        except:
            pass

        os.mkdir(destination) # creates static folder
        os.mkdir(root_files_destination) # creates angular folder

        dirs = os.listdir( origin )

        for _ in dirs:
            root_file = f'{origin}/{_}'

            if _ in folders:
                folder_path = f'{origin}/{_}/'
                nested_folders = os.listdir(folder_path)
                for nest_folder in nested_folders: # checks for folder in dist.
                    f_path = f'{folder_path}{nest_folder}/'
                    destination_path = folders_path.get(f_path)
                    shutil.copytree(f_path,destination_path)  # copies origin folder into destination folder

            elif files_path.get(root_file):  # copies ecma files to desitnation root
                 shutil.copy(root_file,files_path.get(root_file))

            else:
                shutil.copy(root_file,root_files_destination) # copies origin files to destination angular folder.



