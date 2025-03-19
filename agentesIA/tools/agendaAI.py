import os
import sys
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
import re
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from .agendaTool import AgendaReservaTool

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

def reservar_agenda(agenda_id, cliente_id, comentarios="Reservada mediante chatbot"):
    """
    Actualiza una agenda abierta para asignarla a un cliente específico.
    """
    try:
        print("\n=== INICIANDO PROCESO DE RESERVA ===")
        print(f"Intentando reservar agenda ID: {agenda_id} para cliente ID: {cliente_id}")
        
        # Usar la URL específica con el ID de la agenda
        url = f"{BASE_URL}/crm/agendaAbierta/{agenda_id}/"
        print(f"URL de reserva: {url}")
        
        # Primero obtener la agenda actual
        print("Obteniendo datos actuales de la agenda...")
        agendas = obtener_agendas_abiertas()
        agenda = None
        
        for a in agendas:
            if a.get('id') == agenda_id:
                agenda = a
                break
                
        if not agenda:
            print(f"ERROR: No se encontró la agenda con ID {agenda_id}")
            return {
                "success": False,
                "message": f"No se encontró la agenda con ID {agenda_id}"
            }
            
        print(f"Agenda encontrada: {agenda}")
        
        # Preparar datos para actualización
        data = {
            "agente": agenda.get('agente'),
            "fecha": agenda.get('fecha'),
            "hora": agenda.get('hora'),
            "cliente": cliente_id,
            "disponible": False,
            "comentarios": comentarios
        }
        print(f"Datos preparados para actualización: {data}")
        
        # Realizar la solicitud PUT
        print("Enviando solicitud PUT para actualizar agenda...")
        response = requests.put(url, json=data)
        print(f"Código de respuesta: {response.status_code}")
        print(f"Respuesta del servidor: {response.text}")
        
        if response.status_code == 200:
            print("¡Reserva exitosa!")
            return {
                "success": True,
                "message": "Agenda reservada exitosamente",
                "data": response.json()
            }
        else:
            print(f"ERROR: La reserva falló con código {response.status_code}")
            return {
                "success": False,
                "message": f"Error al reservar agenda: {response.status_code}",
                "error": response.text
            }
    except Exception as e:
        print(f"ERROR CRÍTICO en reservar_agenda: {str(e)}")
        return {
            "success": False,
            "message": f"Error al reservar agenda: {str(e)}"
        }

class AgenteAgenda:
    def __init__(self, cliente_id=None):
        # Inicializar la memoria de la conversación
        self.memory = ConversationBufferMemory()
        
        # Inicializar el modelo de lenguaje
        self.llm = ChatOpenAI(
            model_name="gpt-4o-mini", 
            temperature=0.7, 
            openai_api_key=OPENAI_API_KEY
        )
        
        # Estado del agente
        self.ultima_consulta_agendas = None
        self.agendas_cache = None
        
        # Establecer el ID del cliente desde el inicio
        self.cliente_id = cliente_id
        
        # Inicializar herramientas
        self.tools = [
            AgendaReservaTool(cliente_id=cliente_id),
        ]
        
        # Inicializar el agente
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            memory=self.memory,
            handle_parsing_errors=True
        )
    
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
        Procesa el mensaje del usuario usando el agente de LangChain.
        """
        print("\n=== PROCESANDO MENSAJE DEL USUARIO ===")
        print(f"Mensaje recibido: {mensaje_usuario}")
        print(f"Cliente ID actual: {self.cliente_id}")
        
        try:
            # Obtener agendas disponibles
            agendas = obtener_agendas_abiertas()
            
            # Crear el contexto para el agente
            contexto = f"""
            Eres un asistente virtual especializado en agendas inmobiliarias.
            
            Instrucciones importantes:
            1. SIEMPRE muestra las agendas disponibles cuando el usuario pregunte por ellas o quiera hacer una reserva.
            2. NO reserves ninguna agenda hasta que el usuario especifique explícitamente el ID que desea reservar.
            3. El formato para que el usuario reserve debe ser "quiero reservar/separar la agenda id=X" donde X es el número.
            
            Agendas disponibles:
            {formatear_agendas(agendas)}
            
            Cliente actual ID: {self.cliente_id}
            
            Si el usuario quiere reservar una agenda:
            1. Si no especifica ID, muestra las agendas disponibles y pide que elija una por su ID
            2. Si especifica ID (formato: id=X), usa la herramienta reservar_agenda
            3. Confirma el resultado al usuario
            
            No pidas el ID del cliente, ya lo tenemos: {self.cliente_id}
            """
            
            # Ejecutar el agente con el contexto
            respuesta = self.agent.run(f"{contexto}\n\nUsuario: {mensaje_usuario}")
            
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
