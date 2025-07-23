# -*- coding: utf-8 -*-

# Importaciones necesarias para el funcionamiento del módulo.
from . import scibert_model  # Modelo SciBERT para procesamiento de texto científico.
from . import ocr_model  # Modelo OCR para extracción de texto de imágenes/PDF.
from azure.ai.inference.models import SystemMessage, UserMessage  # Clases para mensajes de sistema y usuario en Azure AI.
from google.cloud import vision  # Cliente de Google Cloud Vision para OCR.
import json  # Para trabajar con datos en formato JSON.
import re  # Para operaciones con expresiones regulares.
import uuid  # Para generar identificadores únicos.
import torch  # Biblioteca de PyTorch para machine learning.

# --- Constantes de Configuración ---
SUMMARY_RATIO = 0.1  # Proporción para resúmenes (actualmente no se usa directamente).
BUCKET_NAME = "scibot-backend"  # Nombre del bucket en Google Cloud Storage.
FILES_FOLDER = "ocr_documents"  # Carpeta para almacenar los documentos PDF subidos.
OUTPUT_FOLDER = "ocr_output"  # Carpeta para almacenar los resultados del OCR.

# --- Clientes de Servicios Externos ---
# Se inicializan los clientes para interactuar con Google Cloud Storage y Vision.
storage_client = ocr_model.storage_client
ocr_client = ocr_model.ocr_client

def list_files():
    """
    Lista los archivos de resultados de OCR almacenados en el bucket.
    Recorre los blobs (archivos) en la carpeta de salida de OCR,
    descarga su contenido y lo imprime en la consola.
    Esta función es útil para depuración.
    """
    blob_list = storage_client.list_blobs(BUCKET_NAME, prefix=f"{OUTPUT_FOLDER}")
    print(blob_list)
    for blob in blob_list:
        json_string = blob.download_as_bytes().decode("utf-8")
        print(json_string)
        try:
            # Intenta cargar el JSON y extraer la anotación de texto completo.
            response = json.loads(json_string)
            annotation = response["responses"][0]["fullTextAnnotation"]
        except:
            # Si falla, simplemente continúa con el siguiente archivo.
            pass

def load_file_to_bucket(uploaded_pdf):
    """
    Sube un archivo PDF al bucket de Google Cloud Storage.
    Args:
        uploaded_pdf (File): El archivo PDF subido por el usuario.
    Returns:
        str: La URI de GCS (Google Cloud Storage) del archivo subido.
    """
    bucket = storage_client.bucket(BUCKET_NAME)
    # Genera un nombre de archivo único para evitar colisiones.
    filename = f"{FILES_FOLDER}/{uuid.uuid4()}_{uploaded_pdf.name}"
    blob = bucket.blob(filename)

    # Se asegura de que el puntero del archivo esté al inicio antes de subirlo.
    uploaded_pdf.seek(0)
    blob.upload_from_file(uploaded_pdf, content_type=uploaded_pdf.content_type)

    return f"gs://{BUCKET_NAME}/{filename}"

def get_image_data(uploaded_pdf):
    """
    Procesa un archivo PDF para extraer su texto usando Google Cloud Vision OCR.
    Args:
        uploaded_pdf (File): El archivo PDF subido.
    Returns:
        str: El texto extraído del PDF.
    """
    # 1. Sube el PDF al bucket y obtiene su URI.
    gcs_input_uri = load_file_to_bucket(uploaded_pdf)

    # 2. Define la carpeta de salida para los resultados del OCR.
    prefix_folder = f"{OUTPUT_FOLDER}/{uuid.uuid4()}/"
    gcs_output_uri = f"gs://{BUCKET_NAME}/{prefix_folder}"

    mime_type = "application/pdf"
    batch_size = 2  # Número de páginas a procesar en cada lote.

    # 3. Configura la solicitud de OCR.
    feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)
    gcs_source = vision.GcsSource(uri=gcs_input_uri)
    input_config = vision.InputConfig(gcs_source=gcs_source, mime_type=mime_type)

    gcs_destination = vision.GcsDestination(uri=gcs_output_uri)
    output_config = vision.OutputConfig(gcs_destination=gcs_destination, batch_size=batch_size)

    # 4. Crea y envía la solicitud asíncrona de anotación de archivos.
    async_request = vision.AsyncAnnotateFileRequest(
        features=[feature], input_config=input_config, output_config=output_config
    )
    operation = ocr_client.async_batch_annotate_files(requests=[async_request])

    print("Esperando a que termine la operación OCR...")
    operation.result(timeout=420)  # Espera a que la operación se complete.

    # 5. Recopila los resultados del OCR.
    output_text = ""
    blob_list = storage_client.list_blobs(BUCKET_NAME, prefix=prefix_folder)
    for blob in blob_list:
        json_string = blob.download_as_bytes().decode("utf-8")
        try:
            # Carga el JSON y extrae el texto de la anotación.
            response = json.loads(json_string)
            annotation = response["responses"][0]["fullTextAnnotation"]
            output_text += annotation["text"] + " " 
        except:
            # Si hay un error al procesar un archivo de resultado, lo ignora.
            pass

    return output_text

def cleanPdf(text):
    """
    Realiza una limpieza básica del texto extraído.
    Reemplaza los saltos de línea por espacios.
    Args:
        text (str): El texto a limpiar.
    Returns:
        str: El texto limpiado.
    """
    text = text.replace("\n", " ")
    return text

def parse_error(text):
    """
    Analiza un texto de error para extraer un mensaje más legible.
    Busca patrones específicos en el texto del error.
    Args:
        text (str): El texto del error.
    Returns:
        dict: Un diccionario con el mensaje de error formateado.
    """
    try:
        message_match = re.search(r"Message:\s*(.+)", text)
        max_size_match = re.search(r"Max size:\s*(\d+)", text, re.IGNORECASE)

        message = message_match.group(1).strip() if message_match else ""
        max_size = max_size_match.group(1) if max_size_match else ""

        return {"error": f"{message} (Max size: {max_size})"}
    except:
        return {"error": "Error inesperado intenta de nuevo"}

def extract_error_message(error_text):
    """
    Extrae el mensaje de error detallado de una cadena de error que contiene un JSON.
    Args:
        error_text (str): La cadena de texto del error.
    Returns:
        str: El mensaje de error extraído o un mensaje de fallo.
    """
    try:
        # Busca una subcadena que parezca un diccionario.
        match = re.search(r"(\'{.*?\}')", error_text, re.DOTALL)
        
        # Limpia la cadena para que sea un JSON válido.
        error_text = match.group(1)
        error_text = error_text.replace("'{", "{")
        error_text = error_text.replace("}'", "}")
        error_dict = json.loads(error_text)
  
        # Extrae el valor de la clave 'detail'.
        if 'detail' in error_dict:
            detail = error_dict['detail']
            return detail
    
    except (AttributeError, ValueError, SyntaxError):
        return "Failed to parse error message"
    
def summarize_data(text, model):
    """
    Genera un resumen de un texto utilizando un modelo de lenguaje de Azure AI.
    Args:
        text (str): El texto a resumir.
        model (str): El identificador del modelo a utilizar.
    Returns:
        dict: Un diccionario con el resumen o un mensaje de error.
    """
    base_prompt = '''
    Como sistema de IA, asegúrese de que sus respuestas sean imparciales, éticas y cumplan con las regulaciones de la IA.
    Eres un científico experto que puede generar resúmenes con ideas clave claras y concisas sobre un tema específico. Se te entrega un trabajo de tesis universitario de Ecuador que puede ser de diversas áreas de ciencias. Debes realizar un resumen de una extensión de 500 palabras del artículo. El contenido debe ser formal, instructivo y la estructura del resumen debe ser en ideas principales, con palabras clave.
    '''
    print(model)
    
    try:
        # Realiza la llamada al API de chat de Azure AI.
        response = scibert_model.client.chat.completions.create(
            messages=[{"role": "user", "content": f"{base_prompt}: {text}"}],
            temperature=0.7,
            top_p=1,
            model=model,
            timeout=600
        )
        summary = response.choices[0].message.content
        return {"summary": summary}
    except Exception as e:
        print(e)
        return extract_error_message(str(e))
    
def answer_question(history, question, model="mistralai/mistral-nemo:free"):
    """
    Responde una pregunta basada en un historial de conversación y un texto de resumen.
    Args:
        history (list): Una lista de diccionarios con el historial de chat.
        question (str): La pregunta del usuario.
        model (str): El identificador del modelo a utilizar.
    Returns:
        dict: Un diccionario con la respuesta o un mensaje de error.
    """
    base_prompt = '''
    Eres experto respondiendo preguntas únicamente sobre el texto que generaste el resumen.
    Debes responder preguntas únicamente del texto que se te proporcionó. 
    El contenido de las respuestas debe ser formal, instructivo y la estructura de las respuestas debe ser en ideas claras y clave con una extensión de 100 palabras.
    '''

    # Construye el historial de mensajes para el modelo.
    messages = []
    for record in history:
        messages.append(UserMessage(record["user"]))
        messages.append(SystemMessage(record["bot"]))
    
    messages.append(UserMessage(f"{base_prompt}: {question}"))

    try:
        # Realiza la llamada al API de chat.
        response = scibert_model.client.chat.completions.create(
            messages=messages,
            temperature=0.1,
            top_p=1,
            model=model,
        )
        answer = response.choices[0].message.content
        print(answer)
        return {"answer": answer}
    except Exception as e:
        print(e)
        return parse_error(str(e))

def use_mt5_model(texto, max_tokens=384):
    """
    Genera un resumen de un texto utilizando un modelo T5 preentrenado localmente.
    Args:
        texto (str): El texto a resumir.
        max_tokens (int): El número máximo de tokens para el resumen.
    Returns:
        str: El texto del resumen generado.
    """
    # Determina si se usará CPU o GPU.
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Tokeniza el texto de entrada.
    entrada = scibert_model.custom_tokenizer(
        "summarize: " + texto,
        return_tensors="pt",
        truncation=True,
        padding="max_length",
        max_length=1024
    ).to(device)

    # Genera el resumen sin calcular gradientes para ahorrar memoria.
    with torch.no_grad():
        salida = scibert_model.custom_model.generate(
            input_ids=entrada["input_ids"],
            attention_mask=entrada["attention_mask"],
            max_length=max_tokens,
            min_length=32,               # Longitud mínima para evitar resúmenes vacíos.
            num_beams=4,                 # Búsqueda por haces para mejorar la coherencia.
            repetition_penalty=2.0,      # Penaliza la repetición de palabras.
            length_penalty=1.0,          # Sin penalización por longitud.
            early_stopping=True          # Detiene la generación cuando se alcanza un buen resultado.
        )

    # Decodifica la salida para obtener el texto del resumen.
    resumen = scibert_model.custom_tokenizer.decode(salida[0], skip_special_tokens=False)
    return resumen
