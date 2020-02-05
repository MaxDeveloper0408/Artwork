from django.apps import AppConfig


class ArtsConfig(AppConfig):
    name = 'arts'

    def ready(self):
        import arts.signals
