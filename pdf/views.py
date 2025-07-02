from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pdf.models import Conversation
import pdfplumber
from . import utils
import uuid
import json

@csrf_exempt
def loadPdf(request):
    if request.method == "POST":
        
        uploaded_pdf = request.FILES.get('pdf')
        if uploaded_pdf:
            try:
                model = request.GET.get('model')
                with pdfplumber.open(uploaded_pdf.file) as pdf:
                    data = ""
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            data += text + ' '
                    if data == "":
                        data = utils.get_image_data(uploaded_pdf)
            except:
                return JsonResponse({"error" : "Error al procesar archivo"}, status=400)
        
        session_id = uuid.uuid4()
        data = utils.cleanPdf(data)
        summary = utils.summarize_data(data, model)

        Conversation.objects.create(
            session_id=session_id,
            user_message=data,
            bot_response=summary
        )

        return JsonResponse({"session_id" : session_id , "summary":summary}, status=200)
    else:   
        return HttpResponse("Methodo invalido, solo POST requests", status=405)


@csrf_exempt
def chat(request):
    if request.method == "POST":
        try: 
            session_id = request.GET.get('session_id')
            model = request.GET.get('model')
        except:
            return JsonResponse({"error":"No se puede encontrar el session ID nor model"}, status=404)

        try:
            data = json.loads(request.body)
            user_message = data.get("message")  # O el nombre del campo que esperas
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        conversations = Conversation.objects.filter(session_id=session_id).order_by("timestamp")
        data = [
            {
                "user": conv.user_message,
                "bot": conv.bot_response,
                "timestamp": conv.timestamp.isoformat()
            }
            for conv in conversations
        ]
        answer = utils.answer_question(data, user_message, model)
        
        Conversation.objects.create(
            session_id=session_id,
            user_message=user_message,
            bot_response=answer
        )

        return JsonResponse({"answer":answer}, status=200)
    else:   
        return HttpResponse("Methodo invalido, solo POST requests", status=405)