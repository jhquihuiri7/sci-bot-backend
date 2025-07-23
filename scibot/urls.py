# -*- coding: utf-8 -*-

"""
Configuración de URL para el proyecto scibot.

Este archivo es el enrutador principal del proyecto Django. Mapea las rutas de URL
a las funciones de vista (views) que manejan las solicitudes HTTP.

Para más información, consulta la documentación de Django sobre URLs:
https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

# --- Importaciones de Django y de la aplicación ---
from django.contrib import admin  # Módulo de administración de Django.
from django.urls import path  # Función para definir rutas de URL.
from pdf.views import loadPdf, chat  # Importa las vistas específicas de la aplicación 'pdf'.

# --- Lista de Patrones de URL (urlpatterns) ---
# Esta lista contiene todas las rutas de URL que la aplicación reconocerá.
# Django procesa esta lista en orden y utiliza la primera coincidencia que encuentra.
urlpatterns = [
    # URL para la interfaz de administración de Django.
    # Ejemplo: http://127.0.0.1:8000/admin/
    path('admin/', admin.site.urls),

    # URL para la vista `loadPdf`. Esta vista maneja la carga y el procesamiento
    # inicial de los archivos PDF.
    # Ejemplo: http://127.0.0.1:8000/load
    path('load', loadPdf),

    # URL para la vista `chat`. Esta vista maneja la conversación interactiva
    # después de que un PDF ha sido procesado.
    # Ejemplo: http://127.0.0.1:8000/chat
    path('chat', chat)
]
