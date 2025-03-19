import os
import sys
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI

# Configurar salida estándar a UTF-8 para evitar problemas de codificación en la terminal
sys.stdout.reconfigure(encoding='utf-8')

# Cargar variables de entorno
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

def obtener_agendas_abiertas():
    """
    Llama a la API para obtener las agendas abiertas.
    """
    try:
        url = f"{BASE_URL}/crm/agendaAbierta/"
        response = requests.get(url)
        response.raise_for_status()  # Lanza una excepción si hay error HTTP
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la API: {e}")
        return f"Error al conectar con la API: {e}"

def formatear_agendas(agendas):
    """Formatea la información de las agendas para presentarla de manera legible."""
    if isinstance(agendas, str):  # Si es un mensaje de error
        return agendas
    
    if not agendas:
        return "No hay agendas abiertas disponibles en este momento."
    
    resultado = "Estas son las agendas inmobiliarias disponibles:\n\n"
    
    for agenda in agendas:
        try:
            # Extraer datos con manejo seguro de tipos
            agenda_id = agenda.get('id', 'N/A')
            fecha = agenda.get('fecha', 'N/A')
            hora = agenda.get('hora', 'N/A')
            estado = agenda.get('estado', 'N/A')
            
            resultado += f"- ID: {agenda_id}\n"
            resultado += f"  Fecha: {fecha}\n"
            resultado += f"  Hora: {hora}\n"
            
            if estado:
                resultado += f"  Estado: {estado}\n"
            
            # Verificar si propiedad es un diccionario
            propiedad = agenda.get('propiedad', {})
            if isinstance(propiedad, dict) and propiedad:
                resultado += f"  Propiedad: {propiedad.get('nombre', 'N/A')}\n"
            elif propiedad:
                resultado += f"  Propiedad ID: {propiedad}\n"
            
            # Verificar si agente es un diccionario
            agente = agenda.get('agente', {})
            if isinstance(agente, dict) and agente:
                resultado += f"  Agente: {agente.get('nombre', 'N/A')}\n"
            elif agente:
                resultado += f"  Agente ID: {agente}\n"
            
            resultado += "\n"
        except Exception as e:
                # En caso de error al formatear una agenda, continuar con la siguiente
                print(f"Error al formatear agenda: {e}")
                continue
        
    return resultado

class AgenteAgenda:
    def __init__(self):
        # Inicializar la memoria de la conversación
        self.memory = ConversationBufferMemory()
        
        # Inicializar el modelo de lenguaje
        self.llm = ChatOpenAI(
            model_name="gpt-4", 
            temperature=0.7, 
            openai_api_key=OPENAI_API_KEY
        )
        
        # Estado del agente
        self.ultima_consulta_agendas = None
        self.agendas_cache = None
    
    def reset(self):
        """Reinicia la conversación y las respuestas"""
        self.memory = ConversationBufferMemory()
        self.ultima_consulta_agendas = None
        self.agendas_cache = None
    
    def generar_respuesta_natural(self, mensaje_usuario, agendas=None):
        """
        Genera una respuesta natural basada en el historial de conversación
        y los datos de agendas si están disponibles.
        """
        # Obtener el historial de la conversación
        historial = self.memory.load_memory_variables({})
        historial_str = historial.get("history", "")
        
        # Preparar la información de agendas si está disponible
        info_agendas = ""
        if agendas is not None:
            try:
                info_agendas = formatear_agendas(agendas)
                # Cache de las agendas para futuras preguntas
                self.agendas_cache = agendas
                self.ultima_consulta_agendas = datetime.now()
            except Exception as e:
                print(f"Error al formatear agendas: {e}")
                info_agendas = "Error al procesar las agendas disponibles."
        
        # Fecha y hora actual
        fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Construir el prompt para el LLM
        prompt = (
            f"Eres un asistente virtual inmobiliario especializado en agendas. Actúa de manera natural y conversacional.\n\n"
            f"Historial de conversación:\n{historial_str}\n\n"
            f"Mensaje del usuario: {mensaje_usuario}\n\n"
        )
        
        # Añadir información de agendas si está disponible
        if info_agendas:
            prompt += f"Información de agendas disponibles:\n{info_agendas}\n\n"
        
        prompt += (
            f"La fecha y hora actual es: {fecha_hora_actual}\n\n"
            f"Responde de manera amigable y conversacional. Si el usuario solicita información sobre agendas, "
            f"proporciona detalles específicos basados en la información de agendas disponible. "
            f"Si el usuario se presenta, responde cordialmente y pregúntale en qué puedes ayudarle. "
            f"SIEMPRE ten presente la fecha y hora actual en tu respuesta sin necesidad de mencionarlo."
        )
        
        try:
            # Generar respuesta con el LLM
            respuesta = self.llm.predict(prompt)
            return respuesta
        except Exception as e:
            print(f"Error al generar respuesta: {e}")
            return f"Lo siento, estoy teniendo dificultades para procesar tu solicitud. La fecha actual es {fecha_hora_actual}."
        
    def procesar_mensaje(self, mensaje_usuario):
        """
        Procesa el mensaje del usuario y decide si necesita consultar las agendas.
        """
        if not mensaje_usuario or not mensaje_usuario.strip():
            return {
                "tipo": "respuesta",
                "mensaje": "Por favor, introduce una consulta válida sobre agendas inmobiliarias."
            }
        
        try:
            # Verificar si es necesario consultar agendas
            palabras_clave = ["agenda", "horario", "disponible", "disponibilidad", "fecha", "fechas", 
                            "hora", "horas", "propiedad", "propiedades", "inmueble", "inmuebles", 
                            "visita", "visitar", "cita", "coordinar", "programar"]
            
            debe_consultar = any(palabra in mensaje_usuario.lower() for palabra in palabras_clave)
            
            # También consultar si ha pasado cierto tiempo desde la última consulta
            tiempo_transcurrido = datetime.now() - self.ultima_consulta_agendas if self.ultima_consulta_agendas else None
            consulta_expirada = tiempo_transcurrido and tiempo_transcurrido.total_seconds() > 300  # 5 minutos
            
            agendas = None
            # Consultar agendas si es necesario
            if debe_consultar or consulta_expirada or self.agendas_cache is None:
                try:
                    print("Consultando agendas en el backend...")
                    agendas = obtener_agendas_abiertas()
                except Exception as e:
                    print(f"Error al obtener agendas: {e}")
                    return {
                        "tipo": "error",
                        "mensaje": f"Lo siento, ocurrió un error al obtener las agendas. Por favor, intenta más tarde."
                    }
            else:
                # Usar las agendas en caché
                agendas = self.agendas_cache
            
            # Guardar el mensaje del usuario en la memoria
            self.memory.save_context(
                {"input": mensaje_usuario},
                {"output": ""}  # Guardaremos la respuesta después de generarla
            )
            
            # Generar respuesta natural
            respuesta = self.generar_respuesta_natural(mensaje_usuario, agendas)
            
            # Guardar la respuesta en la memoria
            self.memory.save_context(
                {"input": ""},  # Ya guardamos el input antes
                {"output": respuesta}
            )
            
            return {
                "tipo": "respuesta",
                "mensaje": respuesta
            }
        except Exception as e:
            print(f"Error en procesar_mensaje: {e}")
            return {
                "tipo": "error",
                "mensaje": "Lo siento, ocurrió un error inesperado. Por favor, intenta de nuevo."
            }

def chatear_con_agente():
    agente = AgenteAgenda()
    print("Agente de Agendas: ¡Hola! Soy tu asistente virtual de agendas inmobiliarias. ¿En qué puedo ayudarte hoy?")
    
    while True:
        try:
            user_input = input("Tú: ")
            if not user_input.strip():
                continue
                
            if user_input.lower() in ["salir", "exit", "adiós", "adios", "chau"]:
                print("Agente de Agendas: ¡Gracias por tu consulta! Que tengas un excelente día.")
                break  # Solo salir del bucle cuando el usuario se despide
                
            respuesta = agente.procesar_mensaje(user_input)
            print(f"Agente de Agendas: {respuesta['mensaje']}")
        except Exception as e:
            print(f"Error en el ciclo principal: {e}")
            print("Agente de Agendas: Lo siento, ocurrió un error. Por favor, intenta de nuevo.")

# Eliminar o comentar esta parte
# if __name__ == "__main__":
#     chatear_con_agente()
