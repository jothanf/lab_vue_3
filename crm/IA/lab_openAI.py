from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate_property_description(self, property_data):
        try:
            prompt = self._create_property_prompt(property_data)
            
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": """Eres un experto agente inmobiliario con años de experiencia.
                        Tu tarea es crear descripciones profesionales y atractivas de propiedades,
                        destacando sus características más relevantes y su potencial."""
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500
            )
            
            return {
                "success": True,
                "description": completion.choices[0].message.content
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _create_property_prompt(self, data):
        amenidades = data.get('amenidades', [])
        edificio = data.get('edificio', {})
        
        return f"""
        Crea una descripción atractiva y profesional para una propiedad con las siguientes características:

        INFORMACIÓN BÁSICA:
        - Tipo: {data.get('tipo_propiedad', 'No especificado')}
        - Área construida: {data.get('metro_cuadrado_construido', 0)} m²
        - Habitaciones: {data.get('habitaciones', 0)}
        - Baños: {data.get('banos', 0)}
        - Nivel: {data.get('nivel', 'No especificado')}
        
        UBICACIÓN:
        - Edificio: {edificio.get('nombre', 'No especificado')}
        - Dirección: {data.get('direccion', {}).get('direccion', 'No especificada')}
        - Estrato: {data.get('estrato', 'No especificado')}
        
        AMENIDADES:
        {', '.join([a['nombre'] for a in amenidades]) if amenidades else 'No especificadas'}
        
        INFORMACIÓN FINANCIERA:
        - Valor Administración: ${data.get('valor_administracion', 0):,}
        - Modalidad de negocio: {self._format_business_mode(data.get('modalidad_de_negocio', {}))}

        La descripción debe ser profesional, destacar los puntos fuertes y usar un tono persuasivo.
        Incluye menciones sobre la ubicación, comodidades y características que la hacen única.
        """

    def _format_business_mode(self, modalidad):
        modes = []
        if modalidad.get('venta_tradicional', {}).get('activo'):
            modes.append(f"Venta por ${modalidad['venta_tradicional']['precio']}")
        if modalidad.get('renta_tradicional', {}).get('activo'):
            modes.append(f"Renta por ${modalidad['renta_tradicional']['precio']}")
        return ' y '.join(modes) if modes else 'No especificada'
    