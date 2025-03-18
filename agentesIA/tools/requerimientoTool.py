from langchain.tools import BaseTool
from typing import Dict, Any, Optional, Type, ClassVar, List
from pydantic import BaseModel, Field
import re
import random

class RequerimientoInput(BaseModel):
    """Esquema para la entrada de la herramienta de requerimiento inmobiliario."""
    mensaje: str = Field(description="Mensaje del usuario sobre sus necesidades inmobiliarias")
    historial_conversacion: Optional[list] = Field(description="Historial de la conversación", default=[])
    datos_recopilados: Optional[Dict[str, Any]] = Field(description="Datos ya recopilados del requerimiento", default={})

class RequerimientoTool(BaseTool):
    name: str = "requerimiento_inmobiliario"
    description: str = "Herramienta para mantener una conversación natural con el usuario sobre sus necesidades inmobiliarias"
    args_schema: Type[BaseModel] = RequerimientoInput
    return_direct: bool = False
    
    # Definir la personalidad y contexto de NORA con anotación de tipo ClassVar
    personalidad: ClassVar[Dict[str, Any]] = {
        "nombre": "NORA",
        "rol": "asistente inmobiliaria profesional",
        "tono": "amigable, profesional y empatica",
        "conocimientos": ["mercado inmobiliario", "tipos de propiedades", "zonas residenciales", "procesos de compra/venta"],
        "objetivo": "ayudar a los usuarios a encontrar la propiedad ideal segun sus necesidades",
        "caracteristicas": ["paciente", "detallista", "conocedora del mercado", "orientada al cliente"]
    }
    
    # Variaciones de respuestas para diferentes situaciones con anotación de tipo ClassVar
    variaciones_respuestas: ClassVar[Dict[str, List[str]]] = {
        "saludos": [
            "¡Hola! Soy NORA, tu asistente inmobiliaria. ¿En qué puedo ayudarte hoy con tu búsqueda de propiedades?",
            "¡Bienvenido! Me llamo NORA y estoy aquí para ayudarte a encontrar tu propiedad ideal. ¿Qué estás buscando?",
            "Hola, soy NORA. Encantada de conocerte. Cuéntame, ¿qué tipo de propiedad estás buscando?",
            "¡Saludos! Soy NORA, tu asesora inmobiliaria virtual. ¿Cómo puedo ayudarte en tu búsqueda de propiedades?",
            "Hola, gracias por contactarme. Soy NORA y mi especialidad es ayudar a personas como tú a encontrar la propiedad perfecta. ¿Qué tienes en mente?"
        ],
        "tipo_negocio": [
            "Para ayudarte mejor, me gustaría saber si estás interesado en comprar, alquilar o invertir en una propiedad.",
            "¿Estás pensando en comprar, alquilar o tal vez invertir en bienes raíces? Esto me ayudará a orientar mejor nuestra conversación.",
            "¿Cuál es tu objetivo principal? ¿Comprar una propiedad, alquilarla o hacer una inversión inmobiliaria?",
            "Para ofrecerte la mejor asesoría, ¿podrías decirme si buscas comprar, arrendar o invertir en el sector inmobiliario?",
            "¿Tu interés es comprar una propiedad, arrendarla o estás considerando una inversión inmobiliaria?"
        ],
        "tipo_propiedad_compra": [
            "Entiendo que estás buscando comprar. ¿Qué tipo de propiedad tienes en mente? ¿Un apartamento, casa, oficina o terreno?",
            "Perfecto, estás interesado en comprar. ¿Qué tipo de inmueble estás considerando? ¿Apartamento, casa, o tal vez algo comercial?",
            "Genial, buscar una propiedad para comprar es emocionante. ¿Has pensado en qué tipo de propiedad te gustaría? ¿Casa, apartamento u otro tipo?",
            "Comprar una propiedad es una gran decisión. ¿Ya sabes qué tipo de inmueble prefieres? ¿Apartamento, casa, oficina o terreno?",
            "Para tu compra, ¿qué tipo de propiedad estás considerando? Las opciones más comunes son apartamentos, casas, oficinas o terrenos."
        ]
    }
    
    def _run(self, mensaje: str, historial_conversacion: Optional[list] = None, 
             datos_recopilados: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Ejecuta la herramienta de requerimiento inmobiliario con un enfoque conversacional natural.
        """
        if historial_conversacion is None:
            historial_conversacion = []
        
        if datos_recopilados is None:
            datos_recopilados = {}
        
        # Añadir mensaje del usuario al historial
        historial_conversacion.append({"role": "user", "content": mensaje})
        
        # Extraer información del mensaje
        datos_actualizados = self._extraer_informacion(mensaje, datos_recopilados)
        
        # Analizar el mensaje y generar una respuesta natural
        respuesta = self._generar_respuesta_natural(mensaje, historial_conversacion, datos_actualizados)
        
        # Añadir respuesta del asistente al historial
        historial_conversacion.append({"role": "assistant", "content": respuesta})
        
        return {
            "respuesta": respuesta,
            "historial_conversacion": historial_conversacion,
            "datos_recopilados": datos_actualizados
        }
    
    def _extraer_informacion(self, mensaje: str, datos_recopilados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrae información relevante del mensaje del usuario y actualiza el diccionario de datos.
        """
        # Copia los datos existentes para no modificar el original
        datos = datos_recopilados.copy()
        mensaje_lower = mensaje.lower()
        
        # Detectar tipo de negocio (compra, arriendo, inversión)
        if "tipo_negocio" not in datos:
            if any(palabra in mensaje_lower for palabra in ["comprar", "compra", "adquirir", "adquisición"]):
                datos["tipo_negocio"] = "compra"
            elif any(palabra in mensaje_lower for palabra in ["alquilar", "arrendar", "renta", "alquiler", "arriendo"]):
                datos["tipo_negocio"] = "arriendo"
            elif any(palabra in mensaje_lower for palabra in ["invertir", "inversión"]):
                datos["tipo_negocio"] = "inversión"
        
        # Detectar tipo de propiedad
        if "tipo_propiedad" not in datos:
            if any(palabra in mensaje_lower for palabra in ["apartamento", "apto", "apartaestudio"]):
                datos["tipo_propiedad"] = "apartamento"
            elif any(palabra in mensaje_lower for palabra in ["casa", "vivienda"]):
                datos["tipo_propiedad"] = "casa"
            elif any(palabra in mensaje_lower for palabra in ["oficina", "local", "comercial"]):
                datos["tipo_propiedad"] = "comercial"
            elif any(palabra in mensaje_lower for palabra in ["lote", "terreno"]):
                datos["tipo_propiedad"] = "lote"
        
        # Detectar ubicación
        if "ubicacion" not in datos:
            ubicaciones = re.findall(r'(?:en|cerca de|por|zona|barrio|sector)\s+([A-Za-zÁáÉéÍíÓóÚúÑñ\s]+?)(?:\.|\,|\s+y|\s+o|\s+para|\s+que|\s+con|\s+es|\s+está|\s+tiene|\s+si|\s+no|\s+$)', mensaje_lower)
            if ubicaciones:
                datos["ubicacion"] = ubicaciones[0].strip()
        
        # Detectar presupuesto
        if "presupuesto" not in datos:
            # Buscar patrones como "200 millones", "200.000.000", "entre 100 y 200 millones"
            patrones_presupuesto = [
                r'(\d+)\s*millones',
                r'(\d+[\.\,]?\d*)\s*millones',
                r'(\d+)[\.\,](\d{3})[\.\,](\d{3})',
                r'entre\s+(\d+)\s+y\s+(\d+)\s*millones'
            ]
            
            for patron in patrones_presupuesto:
                match = re.search(patron, mensaje_lower)
                if match:
                    if patron == r'entre\s+(\d+)\s+y\s+(\d+)\s*millones':
                        min_valor = int(match.group(1)) * 1000000
                        max_valor = int(match.group(2)) * 1000000
                        datos["presupuesto"] = {"minimo": min_valor, "maximo": max_valor}
                    elif patron == r'(\d+)[\.\,](\d{3})[\.\,](\d{3})':
                        valor = int(match.group(1) + match.group(2) + match.group(3))
                        datos["presupuesto"] = {"maximo": valor}
                    else:
                        valor = float(match.group(1).replace(',', '.')) * 1000000
                        datos["presupuesto"] = {"maximo": int(valor)}
        
        # Detectar número de habitaciones
        if "habitaciones" not in datos:
            match = re.search(r'(\d+)\s*(?:habitacion|habitaciones|cuarto|cuartos|alcoba|alcobas)', mensaje_lower)
            if match:
                datos["habitaciones"] = int(match.group(1))
    
        # Detectar número de baños
        if "banos" not in datos:
            match = re.search(r'(\d+)\s*(?:baño|baños)', mensaje_lower)
            if match:
                datos["banos"] = int(match.group(1))
        
        # Detectar área
        if "area" not in datos:
            match = re.search(r'(\d+)\s*(?:m2|metros|metro|metros cuadrados)', mensaje_lower)
            if match:
                datos["area"] = int(match.group(1))
        
        # Detectar información familiar
        if "familia" not in datos:
            if any(palabra in mensaje_lower for palabra in ["familia", "hijo", "hijos", "niño", "niños", "pareja", "esposa", "esposo"]):
                datos["familia"] = True
                
                # Intentar extraer número de personas
                match = re.search(r'(?:somos|vivimos|familia de)\s+(\d+)\s+personas', mensaje_lower)
                if match:
                    datos["num_personas"] = int(match.group(1))
        
        # Detectar mascotas
        if "mascotas" not in datos:
            if any(palabra in mensaje_lower for palabra in ["mascota", "mascotas", "perro", "gato", "animal"]):
                datos["mascotas"] = True
        
        return datos
    
    def _generar_respuesta_natural(self, mensaje: str, historial: list, datos: Dict[str, Any]) -> str:
        """
        Genera una respuesta natural basada en el mensaje del usuario, el historial y los datos recopilados.
        """
        mensaje_lower = mensaje.lower()
        
        # Determinar la intención del usuario y el contexto de la conversación
        intencion = self._determinar_intencion(mensaje_lower, historial, datos)
        
        # Generar una respuesta basada en la intención y el contexto
        if intencion == "saludo":
            return random.choice(self.variaciones_respuestas["saludos"])
        
        elif intencion == "consulta_tipo_negocio":
            return random.choice(self.variaciones_respuestas["tipo_negocio"])
        
        elif intencion == "consulta_tipo_propiedad":
            if datos.get("tipo_negocio") == "compra":
                return random.choice(self.variaciones_respuestas["tipo_propiedad_compra"])
            elif datos.get("tipo_negocio") == "arriendo":
                # Usar variaciones para arriendo si existen, o improvisar
                return f"Entiendo que buscas arrendar. ¿Qué tipo de propiedad te interesa? ¿Un apartamento, casa o quizás algo comercial?"
            else:
                return f"Para tu inversión, ¿qué tipo de propiedad estás considerando? Cada tipo tiene diferentes ventajas y rendimientos."
        
        elif intencion == "consulta_ubicacion":
            tipo_propiedad = datos.get("tipo_propiedad", "propiedad")
            return f"La ubicación es clave en bienes raíces. ¿En qué zona o barrio te gustaría que estuviera la {tipo_propiedad}? Esto influirá mucho en tu experiencia y en el valor futuro."
        
        elif intencion == "consulta_presupuesto":
            tipo_negocio = datos.get("tipo_negocio", "")
            tipo_propiedad = datos.get("tipo_propiedad", "propiedad")
            ubicacion = datos.get("ubicacion", "la zona que buscas")
            
            if tipo_negocio == "compra":
                return f"Hablemos de presupuesto. ¿Cuánto estás considerando invertir en la {tipo_propiedad} en {ubicacion}? Esto me ayudará a mostrarte opciones realistas."
            elif tipo_negocio == "arriendo":
                return f"¿Cuál es tu presupuesto mensual para el arriendo de la {tipo_propiedad} en {ubicacion}? Con esta información podré filtrar las mejores opciones."
            else:
                return f"Para una inversión inmobiliaria en {ubicacion}, ¿cuál es el capital que planeas destinar? Esto determinará el tipo de oportunidades a considerar."
        
        # Si no se identifica una intención específica o faltan datos importantes
        return self._generar_respuesta_por_fase(datos)
    
    def _determinar_intencion(self, mensaje: str, historial: list, datos: Dict[str, Any]) -> str:
        """
        Determina la intención del usuario basada en el mensaje y el contexto.
        """
        # Si es el primer mensaje o un saludo
        if len(historial) <= 1 or any(palabra in mensaje for palabra in ["hola", "buenos días", "buenas tardes", "buenas noches", "saludos"]):
            return "saludo"
        
        # Si pregunta por tipos de propiedades
        if any(frase in mensaje for frase in ["qué tipo", "tipos de", "clase de propiedad", "opciones de vivienda"]):
            return "consulta_tipo_propiedad"
        
        # Si pregunta por zonas o ubicaciones
        if any(frase in mensaje for frase in ["qué zona", "dónde", "ubicación", "barrio", "sector"]):
            return "consulta_ubicacion"
        
        # Si pregunta por precios o presupuesto
        if any(frase in mensaje for frase in ["cuánto cuesta", "precio", "valor", "presupuesto", "cuánto vale"]):
            return "consulta_presupuesto"
        
        # Si no hay tipo de negocio definido
        if "tipo_negocio" not in datos:
            return "consulta_tipo_negocio"
        
        # Si hay tipo de negocio pero no tipo de propiedad
        if "tipo_negocio" in datos and "tipo_propiedad" not in datos:
            return "consulta_tipo_propiedad"
        
        # Si hay tipo de propiedad pero no ubicación
        if "tipo_propiedad" in datos and "ubicacion" not in datos:
            return "consulta_ubicacion"
        
        # Si hay ubicación pero no presupuesto
        if "ubicacion" in datos and "presupuesto" not in datos:
            return "consulta_presupuesto"
        
        # Por defecto, determinar la fase actual
        return "fase_actual"
    
    def _generar_respuesta_por_fase(self, datos: Dict[str, Any]) -> str:
        """
        Genera una respuesta basada en la fase actual de la conversación.
        """
        # Determinar qué información falta y hacer preguntas relevantes
        if "tipo_negocio" not in datos:
            return "Para entender mejor tus necesidades, ¿podrías decirme si estás interesado en comprar, alquilar o invertir en una propiedad?"
        
        if "tipo_propiedad" not in datos:
            tipo_negocio = datos["tipo_negocio"]
            if tipo_negocio == "compra":
                return "¿Qué tipo de propiedad estás buscando comprar? Puedo ayudarte con apartamentos, casas, oficinas o terrenos."
            elif tipo_negocio == "arriendo":
                return "¿Qué tipo de propiedad te gustaría arrendar? ¿Buscas un apartamento, una casa o algo comercial?"
            else:
                return "Para tu inversión, ¿en qué tipo de propiedad estás pensando? Cada opción tiene diferentes perfiles de rentabilidad y riesgo."
        
        if "ubicacion" not in datos:
            tipo_propiedad = datos["tipo_propiedad"]
            return f"¿En qué zona o barrio te gustaría que estuviera ubicada la {tipo_propiedad}? La ubicación es uno de los factores más importantes en bienes raíces."
        
        if "presupuesto" not in datos:
            tipo_negocio = datos["tipo_negocio"]
            tipo_propiedad = datos["tipo_propiedad"]
            ubicacion = datos["ubicacion"]
            
            if tipo_negocio == "compra":
                return f"¿Cuál es tu presupuesto para la compra de la {tipo_propiedad} en {ubicacion}? Esto me ayudará a mostrarte opciones que se ajusten a tus posibilidades económicas."
            elif tipo_negocio == "arriendo":
                return f"¿Cuánto estarías dispuesto a pagar mensualmente por el arriendo de la {tipo_propiedad} en {ubicacion}? Conocer tu presupuesto nos permitirá encontrar opciones adecuadas."
            else:
                return f"¿Cuál es el monto que planeas invertir en la {tipo_propiedad} en {ubicacion}? Esto determinará el tipo de oportunidades que podemos considerar."
        
        # Si ya tenemos bastante información, hacer un resumen
        if "tipo_negocio" in datos and "tipo_propiedad" in datos and "ubicacion" in datos and "presupuesto" in datos:
            resumen = self._generar_resumen(datos)
            return f"Basado en nuestra conversación, entiendo que buscas {resumen}. ¿Hay alguna característica específica adicional que sea importante para ti?"
        
        # Respuesta genérica si no se puede determinar la fase
        return "Gracias por la información. ¿Hay algo más que te gustaría compartir sobre lo que buscas en una propiedad?"
    
    def _generar_resumen(self, datos: Dict[str, Any]) -> str:
        """
        Genera un resumen en lenguaje natural de los datos recopilados.
        """
        partes = []
        
        if "tipo_negocio" in datos:
            if datos["tipo_negocio"] == "compra":
                partes.append("comprar")
            elif datos["tipo_negocio"] == "arriendo":
                partes.append("arrendar")
            else:
                partes.append("invertir en")
        
        if "tipo_propiedad" in datos:
            partes.append(f"una {datos['tipo_propiedad']}")
        
        if "ubicacion" in datos:
            partes.append(f"en {datos['ubicacion']}")
        
        if "presupuesto" in datos:
            if isinstance(datos["presupuesto"], dict):
                if "minimo" in datos["presupuesto"] and "maximo" in datos["presupuesto"]:
                    min_valor = datos["presupuesto"]["minimo"] / 1000000
                    max_valor = datos["presupuesto"]["maximo"] / 1000000
                    partes.append(f"con un presupuesto entre {min_valor} y {max_valor} millones")
                elif "maximo" in datos["presupuesto"]:
                    max_valor = datos["presupuesto"]["maximo"] / 1000000
                    partes.append(f"con un presupuesto de hasta {max_valor} millones")
            else:
                partes.append(f"con un presupuesto de {datos['presupuesto']}")
        
        caracteristicas = []
        if "habitaciones" in datos:
            caracteristicas.append(f"{datos['habitaciones']} habitaciones")
        
        if "banos" in datos:
            caracteristicas.append(f"{datos['banos']} baños")
        
        if "area" in datos:
            caracteristicas.append(f"{datos['area']} metros cuadrados")
        
        if caracteristicas:
            partes.append("que tenga " + ", ".join(caracteristicas))
        
        if "mascotas" in datos and datos["mascotas"]:
            partes.append("que permita mascotas")
        
        return " ".join(partes)

# Función para crear la herramienta
def get_requerimiento_tool():
    return RequerimientoTool()
