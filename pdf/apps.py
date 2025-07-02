from django.apps import AppConfig

class PdfConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pdf'

    def ready(self):
        from .scibert_model import load_scibert
        from .ocr_model import load_ocr_model
        load_scibert()
        load_ocr_model()
