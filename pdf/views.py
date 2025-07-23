# -*- coding: utf-8 -*-

# --- Importaciones de Django y otras bibliotecas ---
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt  # Decorador para eximir de la verificación CSRF.
from pdf.models import Conversation  # Modelo de la base de datos para guardar conversaciones.
import pdfplumber  # Biblioteca para extraer texto de archivos PDF.
from . import utils  # Módulo de utilidades locales (procesamiento de texto, modelos, etc.).
import uuid  # Para generar IDs de sesión únicos.
import json  # Para manejar datos en formato JSON.

@csrf_exempt  # Exime esta vista de la protección CSRF, común para APIs sin estado.
def loadPdf(request):
    """
    Vista para cargar un archivo PDF, procesarlo y generar un resumen inicial.

    Endpoint: /pdf/load/
    Método HTTP: POST

    Recibe un archivo PDF, extrae su texto, genera un resumen utilizando un modelo
    de lenguaje y crea una nueva sesión de conversación.
    """
    if request.method == "POST":
        # Obtiene el archivo PDF subido y el modelo seleccionado de la solicitud.
        uploaded_pdf = request.FILES.get('pdf')
        model = request.GET.get('model')

        if not uploaded_pdf:
            return JsonResponse({"error": "No se proporcionó ningún archivo PDF."}, status=400)

        try:
            # Intenta extraer texto usando pdfplumber.
            with pdfplumber.open(uploaded_pdf) as pdf:
                data = ""
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        data += text + ' '

                # Si pdfplumber no extrae texto (PDF basado en imágenes), usa OCR.
                if not data.strip():
                    data = utils.get_image_data(uploaded_pdf)
        except Exception as e:
            # Captura cualquier error durante el procesamiento del archivo.
            return JsonResponse({"error": f"Error al procesar el archivo: {str(e)}"}, status=400)
        
        # Genera un ID de sesión único.
        session_id = uuid.uuid4()
        # Limpia el texto extraído.
        data = utils.cleanPdf(data)

        # Genera el resumen según el modelo especificado.
        if model == "mt5-small":
            response = utils.use_mt5_model(data)
            summary = response
        else:
            response = utils.summarize_data(data, model)
            # Maneja el caso de que la respuesta sea un error.
            if 'error' in response:
                return JsonResponse({"error": response["error"]}, status=400)
            summary = response.get("summary", "")

        # Guarda la primera interacción (el texto completo y su resumen) en la base de datos.
        Conversation.objects.create(
            session_id=session_id,
            user_message=data,  # Se guarda el texto completo como el "mensaje del usuario".
            bot_response=summary
        )

        # Devuelve el ID de la sesión y el resumen.
        return JsonResponse({"session_id": str(session_id), "summary": summary}, status=200)
    else:   
        return HttpResponse("Método inválido, solo se aceptan peticiones POST.", status=405)


@csrf_exempt
def chat(request):
    """
    Vista para manejar el chat interactivo después de que se ha cargado un PDF.

    Endpoint: /pdf/chat/
    Método HTTP: POST

    Recibe un mensaje del usuario y un ID de sesión, recupera el historial de la
    conversación y genera una respuesta utilizando un modelo de lenguaje.
    """
    if request.method == "POST":
        # Obtiene el ID de sesión y el modelo de los parámetros de la URL.
        session_id = request.GET.get('session_id')
        model = request.GET.get('model')
        if not session_id or not model:
            return JsonResponse({"error": "Falta el 'session_id' o el 'model' en los parámetros."}, status=400)
        
        # Decodifica el cuerpo de la solicitud JSON para obtener el mensaje del usuario.
        try:
            body = json.loads(request.body)
            user_message = body.get("message")
            if not user_message:
                return JsonResponse({"error": "El campo 'message' es obligatorio en el JSON."}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido en el cuerpo de la solicitud."}, status=400)
        
        # Recupera el historial de la conversación desde la base de datos.
        try:
            conversations = Conversation.objects.filter(session_id=session_id).order_by("timestamp")
            history = [
                {"user": conv.user_message, "bot": conv.bot_response}
                for conv in conversations
            ]
        except Exception as e:
            return JsonResponse({"error": f"No se pudo cargar el historial: {str(e)}"}, status=500)

        # Genera una respuesta usando el historial y el nuevo mensaje.
        if model == "mt5-small":
            response = utils.answer_question(history, user_message)
        else:
            response = utils.answer_question(history, user_message, model)

        # Maneja si el modelo devuelve un error.
        if 'error' in response:
            return JsonResponse({"error": response["error"]}, status=400)
        
        answer = response.get("answer", "No se pudo generar una respuesta.")
        
        # Guarda la nueva interacción en la base de datos.
        try:
            Conversation.objects.create(
                session_id=session_id,
                user_message=user_message,
                bot_response=answer
            )
        except Exception as e:
            return JsonResponse({"error": f"No se pudo guardar la respuesta: {str(e)}"}, status=500)

        return JsonResponse({"answer": answer}, status=200)
    else:   
        return HttpResponse("Método inválido, solo se aceptan peticiones POST.", status=405)