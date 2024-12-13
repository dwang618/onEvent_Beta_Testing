from django.apps import AppConfig


class OneventConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "onevent"

    def ready(self):
        import onevent.signals
