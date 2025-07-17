from google.cloud import vision
from google.cloud import storage

ocr_client = None
storage_client = None

def load_ocr_model():
    global ocr_client, storage_client
    if ocr_client is None:
        credentials_path = "./scibot-backend-b5fd3808c145.json"
        ocr_client = vision.ImageAnnotatorClient.from_service_account_file(credentials_path)
        storage_client = storage.Client.from_service_account_json(credentials_path)
