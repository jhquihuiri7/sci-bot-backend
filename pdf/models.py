# -*- coding: utf-8 -*-

# --- Importaciones de Django ---
from django.db import models

class Conversation(models.Model):
    """
    Modelo para almacenar el historial de una conversación entre un usuario y el bot.

    Cada instancia de este modelo representa un único intercambio (un mensaje del
    usuario y la correspondiente respuesta del bot) dentro de una sesión de chat.
    """

    # --- Campos del Modelo ---

    # Identificador de la sesión de chat. Permite agrupar todos los intercambios
    # que pertenecen a la misma conversación. Se usa TextField para flexibilidad.
    session_id = models.TextField()

    # El mensaje enviado por el usuario. En el primer turno de una conversación,
    # este campo almacena el texto completo extraído del PDF.
    user_message = models.TextField()

    # La respuesta generada por el bot. En el primer turno, corresponde al
    # resumen del documento.
    bot_response = models.TextField()

    # Marca de tiempo que registra cuándo se creó el registro en la base de datos.
    # `auto_now_add=True` asegura que este campo se establezca automáticamente
    # solo en el momento de la creación del objeto.
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Representación en cadena del objeto.

        Devuelve una cadena legible que identifica la sesión y la marca de tiempo,
        lo cual es útil en la interfaz de administración de Django.
        """
        return f"Sesión {self.session_id} a las {self.timestamp}"
