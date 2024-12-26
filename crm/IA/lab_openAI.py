from openai import OpenAI
import os
from dotenv import load_dotenv
import base64

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
    
    def analyze_image(self, image_path, analysis_type="ocr"):
        prompt_one = [
            "Eres un experto analista inmobiliario con amplia experiencia en valoración de propiedades. Tu tarea es analizar detalladamente la imagen proporcionada y generar una descripción profesional y cautivadora.",
            "IDENTIFICACIÓN INICIAL: Identifica el tipo de espacio o elemento mostrado en la imagen, determina su función principal dentro de la propiedad, observa el contexto general del espacio.",
            "ANÁLISIS DETALLADO: Describe las características físicas principales, identifica materiales visibles y acabados, analiza la iluminación y espacialidad, detecta elementos destacables o únicos, observa el estado de conservación, identifica cualquier elemento de valor agregado.",
            "ELEMENTOS DE CONFORT Y FUNCIONALIDAD: Evalúa la disposición del espacio, identifica elementos que mejoren la habitabilidad, observa características de confort, detecta elementos de automatización o tecnología si están presentes."
        ]
        try:
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode()
                
                # Diferentes prompts según el tipo de análisis
                if analysis_type == "ocr":
                    system_prompt = """Tu única tarea es extraer y transcribir el texto que aparece en la imagen.
                    Solo devuelve el texto encontrado, sin descripciones ni interpretaciones.
                    Si hay números telefónicos, direcciones, nombres o cualquier otro texto, simplemente transcríbelo.
                    No describas la imagen ni su contenido visual."""
                    
                    user_prompt = "Extrae y transcribe todo el texto que veas en esta imagen, incluyendo números y caracteres especiales:"
                else:  # analysis_type == "property"
                    system_prompt = prompt_one
                    
                    user_prompt = "Describe detalladamente esta propiedad desde un punto de vista inmobiliario:"
                
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "\n".join(prompt_one)
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": user_prompt
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}",
                                        "detail": "high"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=500
                )
                
                return response.choices[0].message.content
        except Exception as e:
            print(f"Error al analizar la imagen: {str(e)}")
            return "Error al analizar la imagen"
    