import requests
import json

response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": "Bearer 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",
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