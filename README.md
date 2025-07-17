# SciBot Backend

SciBot is a Django-based backend for a chatbot that can read and summarize PDF documents, and answer questions about their content. It uses different AI models to process the documents and generate responses.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

* Python 3.8 or higher
* pip

### Installing

1. **Clone the repository:**
   ```bash
   git clone https://github.com/georgesepulveda/scibot-backend-challenge.git
   cd scibot-backend-challenge
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
   The server will start on `http://127.0.0.1:8000/`.

## API Documentation

### `POST /load`

This endpoint is used to upload a PDF file. The backend will process the PDF, generate a summary, and create a new conversation session.

**Request:**

*   **Method:** `POST`
*   **URL:** `/load?model=<model_name>`
*   **Headers:** `Content-Type: multipart/form-data`
*   **Query Parameters:**
    *   `model` (string, required): The name of the model to use for summarization.
*   **Body:**
    *   `pdf` (file, required): The PDF file to upload.

**Response:**

*   **Status Code:** `200 OK`
*   **Body:**
    ```json
    {
      "session_id": "a_unique_session_id",
      "summary": "The summary of the PDF content."
    }
    ```

### `POST /chat`

This endpoint is used to send a message to the chatbot and get a response.

**Request:**

*   **Method:** `POST`
*   **URL:** `/chat?session_id=<session_id>&model=<model_name>`
*   **Headers:** `Content-Type: application/json`
*   **Query Parameters:**
    *   `session_id` (string, required): The ID of the conversation session.
    *   `model` (string, required): The name of the model to use for generating the response.
*   **Body:**
    ```json
    {
      "message": "Your question about the document."
    }
    ```

**Response:**

*   **Status Code:** `200 OK`
*   **Body:**
    ```json
    {
      "answer": "The chatbot's answer to your question."
    }
    ```
