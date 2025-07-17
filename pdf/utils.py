from . import scibert_model
from . import ocr_model
from azure.ai.inference.models import SystemMessage, UserMessage
from google.cloud import vision
import json
import re
import uuid

SUMMARY_RATIO = 0.1
BUCKET_NAME = "scibot-backend"
FILES_FOLDER = "ocr_documents"
OUTPUT_FOLDER = "ocr_output"

storage_client = ocr_model.storage_client
ocr_client = ocr_model.ocr_client
def list_files():
    blob_list = storage_client.list_blobs(BUCKET_NAME, prefix=f"{OUTPUT_FOLDER}")
    print(blob_list)
    for blob in blob_list:
        json_string = blob.download_as_bytes().decode("utf-8")
        print(json_string)
        try:
            response = json.loads(json_string)
            annotation = response["responses"][0]["fullTextAnnotation"]
        except:
            pass

def load_file_to_bucket(uploaded_pdf):
    bucket = storage_client.bucket(BUCKET_NAME)
    filename = f"{FILES_FOLDER}/{uuid.uuid4()}_{uploaded_pdf.name}"
    blob = bucket.blob(filename)
    uploaded_pdf.seek(0)
    blob.upload_from_file(uploaded_pdf, content_type=uploaded_pdf.content_type)

    return f"gs://{BUCKET_NAME}/{filename}"

def get_image_data(uploaded_pdf):
    gcs_input_uri = load_file_to_bucket(uploaded_pdf)
    prefix_folder = f"{OUTPUT_FOLDER}/{uuid.uuid4()}/"
    gcs_output_uri = f"gs://{BUCKET_NAME}/{prefix_folder}"

    mime_type = "application/pdf"
    batch_size = 2

    feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)
    gcs_source = vision.GcsSource(uri=gcs_input_uri)
    input_config = vision.InputConfig(gcs_source=gcs_source, mime_type=mime_type)

    gcs_destination = vision.GcsDestination(uri=gcs_output_uri)
    output_config = vision.OutputConfig(gcs_destination=gcs_destination, batch_size=batch_size)

    async_request = vision.AsyncAnnotateFileRequest(
        features=[feature], input_config=input_config, output_config=output_config
    )

    operation = ocr_client.async_batch_annotate_files(requests=[async_request])

    print("Esperando a que termine la operación OCR...")
    operation.result(timeout=420)

    output_text = ""
    blob_list = storage_client.list_blobs(BUCKET_NAME, prefix=prefix_folder)
    for blob in blob_list:
        json_string = blob.download_as_bytes().decode("utf-8")
        try:
            response = json.loads(json_string)
            annotation = response["responses"][0]["fullTextAnnotation"]
            output_text += annotation["text"] + " " 
        except:
            pass

    return output_text

def cleanPdf(text):
    text = text.replace("\n"," ")
    #text = text.replace("\\"," ")
    return text

def parse_error(text):
    try:
        message_match = re.search(r"Message:\s*(.+)", text)
        max_size_match = re.search(r"Max size:\s*(\d+)", text, re.IGNORECASE)

        message = message_match.group(1).strip() if message_match else ""
        max_size = max_size_match.group(1) if max_size_match else ""

        return {
            "error": f"{message} (Max size: {max_size})"
        }
    except:
        return {
            "error": "Error inesperado intenta de nuevo"
        }

import re
import ast

def extract_error_message(error_text):
    """Extracts the error message from the error string."""
    try:
        # Extract the dictionary part from the string
        match = re.search(r"(\'{.*?\}')", error_text, re.DOTALL)
        
        error_text = match.group(1)
        error_text = error_text.replace("'{","{")
        error_text = error_text.replace("}'","}")
        error_dict = json.loads(error_text)
  
        # Navigate to the error detail
        if 'detail' in error_dict:
            detail = error_dict['detail']
            
        return detail
    
    except (AttributeError, ValueError, SyntaxError):
        return "Failed to parse error message"
    
def summarize_data(text, model):
    base_prompt = '''
    Como sistema de IA, asegúrese de que sus respuestas sean imparciales, éticas y cumplan con las regulaciones de la IA.
    Eres un científico experto que puede generar resúmenes con ideas clave claras y concisas sobre un tema específico. Se te entrega un trabajo de tesis universitario de Ecuador que puede ser de diversas áreas de ciencias. Debes realizar un resumen de una extensión de 500 palabras del artículo. El contenido debe ser formal, instructivo y la estructura del resumen debe ser en ideas principales, con palabras clave.
    '''
    print(model)
    
    try:
        response = scibert_model.client.chat.completions.create(
        ##response = scibert_model.client.complete(
            messages=[
                SystemMessage(""),
                UserMessage(f"{base_prompt}: {text}"),
            ],
            temperature=0.7,
            top_p=1,
            model=model
        )

        summary = response.choices[0].message.content

        return {"summary": summary}
    except Exception as e:
        print(e)
        return extract_error_message(str(e))
    

def answer_question(history, question, model):
    base_prompt = '''
    Eres experto respondiendo preguntas únicamente sobre el texto que generaste el resumen.
    Debes responder preguntas únicamente del texto que se te proporcionó. 
    El contenido de las respuestas debe ser formal, instructivo y la estructura de las respuestas debe ser en ideas claras y clave con una extensión de 100 palabras.
    '''

    messages = []
    for record in history:
        messages.append(UserMessage(record["user"]))
        messages.append(SystemMessage(record["bot"]))
    
    messages.append(UserMessage(f"{base_prompt}: {question}"))

    try:
        response = scibert_model.client.chat.completions.create(
        ##response = scibert_model.client.complete(
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

    