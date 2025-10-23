from django.apps import AppConfig


class IzrMediaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "izr_media"
    verbose_name = "IZR Media Management"
    def ready(self):
        import izr_media.signals