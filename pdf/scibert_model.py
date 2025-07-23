# -*- coding: utf-8 -*-

# --- Importaciones ---
# Clases necesarias para interactuar con diferentes APIs de modelos de lenguaje.
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from scibot.settings import MODEL_TOKEN, OPEN_TOKEN, DEBUG  # Tokens y configuraciones desde Django.
from openai import OpenAI  # Cliente de OpenAI para interactuar con APIs compatibles.
from transformers import MT5Tokenizer, MT5ForConditionalGeneration  # Clases de Hugging Face para modelos T5.
import torch  # Biblioteca PyTorch.

# --- Variables Globales para Modelos y Clientes ---
# Se inicializan como None para cargarse una sola vez (patrón Singleton).
client, custom_model, custom_tokenizer = None, None, None

def load_scibert():
    """
    Carga e inicializa los clientes para los modelos de lenguaje y el modelo local T5.

    Esta función se encarga de configurar los clientes para dos servicios de inferencia:
    1. Un endpoint de Azure AI (actualmente comentado y sobreescrito).
    2. La API de OpenRouter, que actúa como un cliente compatible con OpenAI.

    Además, si la aplicación está en modo DEBUG, carga un modelo T5 localmente
    utilizando la biblioteca `transformers` de Hugging Face.

    Utiliza variables globales para asegurar que los modelos y clientes se carguen
    una sola vez.
    """
    global client, custom_model, custom_tokenizer
    
    # --- Configuración del Cliente de Azure AI (Actualmente inactivo) ---
    # Este bloque de código configura un cliente para un endpoint de inferencia,
    # pero es inmediatamente sobreescrito por la configuración de OpenRouter.
    endpoint_azure = "https://models.github.ai/inference"
    client_azure = ChatCompletionsClient(
        endpoint=endpoint_azure,
        credential=AzureKeyCredential(MODEL_TOKEN),
    )

    # --- Configuración del Cliente de OpenRouter (Activo) ---
    # Se utiliza el cliente de OpenAI para conectarse a la API de OpenRouter.
    endpoint_openrouter = "https://openrouter.ai/api/v1"
    global client  # Se asegura de modificar la variable global.
    client = OpenAI(
        base_url=endpoint_openrouter,
        api_key=OPEN_TOKEN,  # Token de autenticación para OpenRouter.
        timeout=60  # Tiempo de espera para las solicitudes.
    )

    # --- Carga del Modelo T5 Local (Solo en modo DEBUG) ---
    # Si la variable DEBUG es True en `settings.py`, se carga un modelo T5.
    if DEBUG:
        # Determina el dispositivo (GPU si está disponible, si no, CPU).
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Ruta al modelo T5 guardado localmente.
        ruta_modelo = "./mt5"

        # Carga el tokenizador y el modelo desde la ruta especificada.
        global custom_tokenizer, custom_model
        custom_tokenizer = MT5Tokenizer.from_pretrained(ruta_modelo)
        custom_model = MT5ForConditionalGeneration.from_pretrained(ruta_modelo)

        # Mueve el modelo al dispositivo seleccionado (GPU/CPU).
        custom_model.to(device)

        # Pone el modelo en modo de evaluación para desactivar capas como Dropout.
        custom_model.eval()

