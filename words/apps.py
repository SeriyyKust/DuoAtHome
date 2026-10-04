from django.apps import AppConfig


class WordsConfig(AppConfig):
    name = 'words'

    def ready(self):
        from . import signals  # noqa: F401
