from django.apps import AppConfig


class AsoronConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'asoron'
    
    def ready(self) -> None:
        import asoron.signals