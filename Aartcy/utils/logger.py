from django.conf import settings
import logging

__all__ = ['Logger']

logger = logging.getLogger(settings.BASE_DIR)



class Logger:

    def __init__(self,message):
        self.message = message

    def warning(self):
        logger.warning(f'\n{self.message}\n')
