from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from scibot.settings import MODEL_TOKEN

client = None

def load_scibert():
    global client
    
    endpoint = "https://models.github.ai/inference"
    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(MODEL_TOKEN),
    )
