import openai
import os
from dotenv import load_dotenv

load_dotenv()  # Asegúrate de que esto esté presente

class AIService:
    def __init__(self):
        self.client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))  # Asegúrate de que la variable de entorno esté bien cargada

    def generate_image(self, dimensions, style="realistic", prompt="", colors=None, quality="standard"):
        try:
            # Validar dimensiones
            if dimensions > 1024:  # Cambia esto a 1024 para cumplir con los requisitos
                raise ValueError("Las dimensiones no pueden ser mayores a 1024.")
            
            size = f"{dimensions}x{dimensions}"  # Asegúrate de que esto sea un tamaño válido
            if size not in ["1024x1024", "1024x1792", "1792x1024"]:
                raise ValueError("Tamaño no soportado. Usa 1024x1024, 1024x1792 o 1792x1024.")
            
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                n=1,
                quality=quality  # Asegúrate de que este argumento esté definido
            )
            
            return {
                "success": True,
                "image_url": response.data[0].url
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }