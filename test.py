import requests
import json

response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": "Bearer TOKEN",
    "Content-Type": "application/json"
  },
  data=json.dumps({
    "model": "nousresearch/deephermes-3-llama-3-8b-preview:free",
    "messages": [
      {
        "role": "user",
        "content": "What is the meaning of life?"
      }
    ],
    
  })
)
print(response.text)