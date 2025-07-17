from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from scibot.settings import MODEL_TOKEN, OPEN_TOKEN
from openai import OpenAI

client = None

def load_scibert():
    global client
    
    endpoint = "https://models.github.ai/inference"
    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(MODEL_TOKEN),
    )

    endpoint = "https://openrouter.ai/api/v1"
    print(OPEN_TOKEN)
    client = OpenAI(
        base_url=endpoint,
        api_key=OPEN_TOKEN,
    )
