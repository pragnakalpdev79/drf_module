from django.apps import AppConfig


class TestingConfig(AppConfig):
    name = 'testing'

    def ready(self):
        import testing.signals
