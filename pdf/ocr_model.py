# -*- coding: utf-8 -*-

# --- Importaciones ---
# Importa las bibliotecas necesarias de Google Cloud.
from google.cloud import vision  # Cliente de la API de Google Cloud Vision para OCR.
from google.cloud import storage  # Cliente de la API de Google Cloud Storage para almacenamiento de archivos.

# --- Variables Globales para los Clientes ---
# Se inicializan como None para que se carguen una sola vez (patrón Singleton).
ocr_client = None
storage_client = None

def load_ocr_model():
    """
    Carga e inicializa los clientes de Google Cloud Vision y Storage.

    Esta función utiliza el patrón Singleton para asegurarse de que los clientes
    se inicialicen solo una vez durante la vida de la aplicación. Esto mejora
    el rendimiento al evitar la reinicialización innecesaria en cada solicitud.

    La función modifica las variables globales `ocr_client` y `storage_client`.
    """
    global ocr_client, storage_client

    # Comprueba si el cliente de OCR ya ha sido inicializado.
    if ocr_client is None:
        # Define la ruta al archivo de credenciales de servicio de Google Cloud.
        # Este archivo es esencial para autenticarse con los servicios de Google.
        credentials_path = "./scibot-backend-b5fd3808c145.json"

        # Inicializa el cliente de ImageAnnotator (OCR) con las credenciales.
        ocr_client = vision.ImageAnnotatorClient.from_service_account_file(credentials_path)

        # Inicializa el cliente de Storage con las mismas credenciales.
        storage_client = storage.Client.from_service_account_json(credentials_path)
