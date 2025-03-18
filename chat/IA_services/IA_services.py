import os
from openai import OpenAI
from dotenv import load_dotenv
import tempfile
import json
from .context_builders import AIContextBuilder


load_dotenv()


class AIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("No se encontró OPENAI_API_KEY en las variables de entorno")
        self.client = OpenAI(api_key=api_key)
        self.context_builder = AIContextBuilder()
        
    def chat_with_gpt(self, user_message, context_type=None, context_data=None):
        try:
            # Construir el mensaje del sistema según el tipo de contexto
            system_message = self._get_context_message(context_type, context_data)
            
            print(f"Enviando mensaje a OpenAI con contexto: {context_type}")
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            error_message = f"Error al comunicarse con OpenAI: {str(e)}"
            print(error_message)
            return error_message

    def _get_context_message(self, context_type, context_data):
        context_builders = {
            'edificio': self.context_builder.build_edificio_context,
            'propiedad': self.context_builder.build_propiedad_context,
            'localidad': self.context_builder.build_localidad_context,
        }
        
        builder = context_builders.get(context_type)
        if builder and context_data:
            return builder(context_data)
        return "Eres un asistente general útil."
  