from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from scibot.settings import MODEL_TOKEN, OPEN_TOKEN, DEBUG
from openai import OpenAI
from transformers import MT5Tokenizer, MT5ForConditionalGeneration
import torch

client, custom_model, custom_tokenizer = None, None, None

def load_scibert():
    global client, custom_model, custom_tokenizer
    
    endpoint = "https://models.github.ai/inference"
    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(MODEL_TOKEN),
    )

    endpoint = "https://openrouter.ai/api/v1"

    client = OpenAI(
        base_url=endpoint,
        api_key=OPEN_TOKEN,
        timeout=60
    )

    if DEBUG:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        ruta_modelo = "./mt5"
        custom_tokenizer = MT5Tokenizer.from_pretrained(ruta_modelo)
        custom_model = MT5ForConditionalGeneration.from_pretrained(ruta_modelo)
        custom_model.to(device)  # Asegura que esté en TPU si estás usándolo
        custom_model.eval()

