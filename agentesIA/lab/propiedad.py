import os
import sys
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
# Importar la herramienta del segundo archivo
import propiedadTool

# Asegurar codificación UTF-8 para la terminal
sys.stdout.reconfigure(encoding='utf-8')

# Cargar variables de entorno
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Lista de aspectos clave a preguntar sobre una propiedad
aspectos = [
    "tipo_propiedad", "titulo", "modalidad_de_negocio", "descripcion", 
    "direccion", "nivel", "metro_cuadrado_construido", "metro_cuadrado_propiedad", 
    "habitaciones", "habitacion_de_servicio", "banos", "terraza", 
    "balcon", "garajes", "depositos", "mascotas"
]

class AgenteInmobiliarioPropiedad:
    def __init__(self):
        # Inicializar la memoria de la conversación
        self.memory = ConversationBufferMemory(memory_key="history")
        
        # Inicializar el modelo de lenguaje con GPT-4
        self.llm = ChatOpenAI(model_name="gpt-4", temperature=0.7, openai_api_key=OPENAI_API_KEY)
        
        # Diccionario para almacenar las respuestas del usuario
        self.respuestas_usuario = {aspecto: None for aspecto in aspectos}
        
        # IDs para la propiedad
        self.agente_id = 12   # Valor por defecto
        self.propietario_id = None  # El propietario puede ser opcional
    
    def set_ids(self, agente_id=None, propietario_id=None):
        """Establece los IDs de agente y propietario para esta propiedad"""
        if agente_id:
            self.agente_id = agente_id
        if propietario_id:
            self.propietario_id = propietario_id
    
    def reset(self):
        """Reinicia la conversación y las respuestas"""
        self.memory = ConversationBufferMemory(memory_key="history")
        self.respuestas_usuario = {aspecto: None for aspecto in aspectos}
        # No reiniciamos los IDs, ya que son específicos de la sesión
    
    def proximo_aspecto(self):
        """Retorna el primer aspecto sin respuesta o None si todos están completos."""
        for aspecto, respuesta in self.respuestas_usuario.items():
            if respuesta is None:
                return aspecto
        return None
    
    def generar_pregunta_natural(self, aspecto):
        """
        Usa el LLM para generar una pregunta natural y conversacional,
        teniendo en cuenta las respuestas previas del usuario.
        """
        historial = self.memory.load_memory_variables({})["history"]
        respuestas_previas = "\n".join(f"{k}: {v}" for k, v in self.respuestas_usuario.items() if v)

        prompt_natural = (
            f"Actúa como un agente inmobiliario experto en registrar propiedades en una plataforma. "
            f"Debes hacer preguntas naturales y contextuales para obtener información sobre una propiedad que el usuario quiere publicar. "
            f"Toma en cuenta la información que el usuario ya proporcionó.\n\n"
            f"Historial de conversación:\n{historial}\n\n"
            f"Respuestas previas del usuario:\n{respuestas_previas}\n\n"
            f"Genera una pregunta NATURAL sobre '{aspecto}' de la propiedad, usando el contexto si es relevante. "
            f"Explica brevemente qué es este aspecto si es técnico o poco claro (como 'metro_cuadrado_construido')."
        )

        pregunta_generada = self.llm.predict(prompt_natural)
        return pregunta_generada
    
    def generar_resumen(self):
        """
        Revisa todo el historial de conversación y las respuestas del usuario para generar un resumen
        natural y descriptivo de la propiedad.
        """
        # Obtener el historial completo de la conversación
        historial = self.memory.load_memory_variables({})["history"]
        
        # Compilar las respuestas proporcionadas por el usuario
        respuestas_previas = "\n".join(f"{aspecto}: {respuesta}" 
                                    for aspecto, respuesta in self.respuestas_usuario.items() 
                                    if respuesta is not None)
        
        # Crear el prompt para que el LLM genere un resumen natural
        prompt_resumen = (
            "Actúa como un agente inmobiliario profesional y elabora un resumen detallado y atractivo "
            "de la propiedad que se va a publicar, basado en la información proporcionada. "
            "Debes incluir los detalles clave, resaltar las características más atractivas, "
            "y presentar la información de forma clara y descriptiva para potenciales compradores o arrendatarios.\n\n"
            f"Historial de conversación:\n{historial}\n\n"
            f"Respuestas del usuario:\n{respuestas_previas}\n\n"
            "Resumen:"
        )
        
        # Usar el LLM para generar el resumen
        resumen = self.llm.predict(prompt_resumen)
        return resumen
    
    def procesar_mensaje(self, mensaje_usuario):
        """
        Procesa un mensaje del usuario y devuelve la respuesta del agente.
        Si el proximo_aspecto es None, significa que todos los aspectos han sido respondidos.
        """
        proximo = self.proximo_aspecto()
        
        if proximo is None:
            # Todos los aspectos han sido respondidos
            resumen = self.generar_resumen()
            return {
                "tipo": "resumen",
                "mensaje": "Gracias, te enseñaré el resumen de la propiedad que vamos a registrar",
                "resumen": resumen,
                "requiere_confirmacion": True
            }
        
        # Si todavía hay aspectos por preguntar
        if not mensaje_usuario:
            # Primer mensaje o reinicio
            saludo = "¡Hola! Te ayudaré a registrar tu propiedad en nuestra plataforma."
            # Generar la primera pregunta inmediatamente
            primera_pregunta = self.generar_pregunta_natural(proximo)
            pregunta_completa = f"{saludo} {primera_pregunta}"
            
            return {
                "tipo": "pregunta",
                "mensaje": pregunta_completa,
                "proximo_aspecto": proximo
            }
        else:
            # Guardar la respuesta del usuario para el aspecto actual
            aspecto_actual = proximo
            self.respuestas_usuario[aspecto_actual] = mensaje_usuario
            
            # Guardar en la memoria de la conversación
            self.memory.save_context({"input": f"Pregunta sobre {aspecto_actual}"}, {"output": mensaje_usuario})
            
            # Obtener el siguiente aspecto
            proximo = self.proximo_aspecto()
            
            if proximo is None:
                # Si ya respondió todos los aspectos
                resumen = self.generar_resumen()
                return {
                    "tipo": "resumen",
                    "mensaje": "Gracias, te enseñaré el resumen de la propiedad que vamos a registrar",
                    "resumen": resumen,
                    "requiere_confirmacion": True
                }
            
            # Generar una pregunta para el próximo aspecto
            pregunta = self.generar_pregunta_natural(proximo)
        
        return {
            "tipo": "pregunta",
            "mensaje": pregunta,
            "proximo_aspecto": proximo
        }
    
    def confirmar_resumen(self, confirmacion):
        """
        Confirma el resumen y registra la propiedad si se confirma.
        Devuelve el resultado de la operación.
        """
        if confirmacion:
            resumen = self.generar_resumen()
            
            print(f"Confirmando resumen de propiedad - Agente ID: {self.agente_id}, Propietario ID: {self.propietario_id}")
            
            # Pasamos los IDs y las respuestas al método agent_tool
            exito, resultado = propiedadTool.agent_tool(
                resumen=resumen,
                respuestas=self.respuestas_usuario,
                agente_id=self.agente_id,
                propietario_id=self.propietario_id
            )
            
            if exito:
                return {
                    "tipo": "confirmacion",
                    "exito": True,
                    "mensaje": "¡La propiedad ha sido registrada exitosamente!",
                    "id": resultado.get("id", "No disponible")
                }
            else:
                return {
                    "tipo": "confirmacion",
                    "exito": False,
                    "mensaje": "Lo siento, hubo un problema al registrar la propiedad.",
                    "error": resultado.get("error", "Desconocido")
                }
        else:
            # Si no confirma, reiniciar aspectos
            return {
                "tipo": "reinicio",
                "mensaje": "Entiendo, ¿deseas modificar algún aspecto de la propiedad?"
            }
    
    def modificar_aspectos(self, aspectos_a_modificar):
        """
        Modifica los aspectos especificados o todos si se indica.
        """
        if aspectos_a_modificar.lower() == "todos":
            # Reiniciar todos los aspectos
            for aspecto in self.respuestas_usuario:
                self.respuestas_usuario[aspecto] = None
        else:
            # Reiniciar solo los aspectos indicados
            for aspecto in aspectos_a_modificar.split(","):
                aspecto = aspecto.strip()
                if aspecto in self.respuestas_usuario:
                    self.respuestas_usuario[aspecto] = None
        
        return {
            "tipo": "modificacion",
            "mensaje": "He reiniciado los aspectos solicitados. Continuemos con la conversación."
        }

# Instancia del agente para uso general
agente_propiedad = AgenteInmobiliarioPropiedad()

# Función para chatear con el agente por consola (para mantener compatibilidad)
def chatear_con_agente():
    print("Agente Inmobiliario: ¡Hola! Te ayudaré a registrar tu propiedad.")
    
    while True:
        proximo = agente_propiedad.proximo_aspecto()
        if proximo is None:
            print("Agente Inmobiliario: Gracias, te enseñaré el resumen de la propiedad")
            resumen = agente_propiedad.generar_resumen()
            print("\nResumen de la propiedad:\n", resumen)
            
            # Preguntar al usuario si el resumen es correcto
            print("\nAgente Inmobiliario: ¿Este resumen es correcto? (sí/no)")
            confirmacion = input("🧑 Tú: ")
            
            if confirmacion.lower() in ["sí", "si", "s", "yes", "y"]:
                print("Agente Inmobiliario: Perfecto, voy a registrar esta propiedad en el sistema...")
                # Usar la función agent_tool del segundo script pasando el resumen
                exito, resultado = propiedadTool.agent_tool(
                    resumen=resumen,
                    respuestas=agente_propiedad.respuestas_usuario
                )
                
                if exito:
                    print("Agente Inmobiliario: ¡La propiedad ha sido registrada exitosamente!")
                    print(f"ID de la propiedad: {resultado.get('id', 'No disponible')}")
                else:
                    print("Agente Inmobiliario: Lo siento, hubo un problema al registrar la propiedad.")
                    print(f"Error: {resultado.get('error', 'Desconocido')}")
                    
                print("Agente Inmobiliario: ¡Gracias por tu tiempo!")
            else:
                print("Agente Inmobiliario: Entiendo, ¿deseas modificar algún aspecto de la propiedad? (sí/no)")
                modificar = input("🧑 Tú: ")
                if modificar.lower() in ["sí", "si", "s", "yes", "y"]:
                    # Reiniciar aspectos específicos o todos
                    print("Agente Inmobiliario: Por favor indícame qué aspectos deseas modificar (separados por coma) o escribe 'todos' para reiniciar:")
                    aspectos_modificar = input("🧑 Tú: ")
                    if aspectos_modificar.lower() == "todos":
                        # Reiniciar todos los aspectos
                        for aspecto in agente_propiedad.respuestas_usuario:
                            agente_propiedad.respuestas_usuario[aspecto] = None
                    else:
                        # Reiniciar solo los aspectos indicados
                        for aspecto in aspectos_modificar.split(","):
                            aspecto = aspecto.strip()
                            if aspecto in agente_propiedad.respuestas_usuario:
                                agente_propiedad.respuestas_usuario[aspecto] = None
                    continue  # Volver al inicio del bucle
                else:
                    print("Agente Inmobiliario: Entendido. No registraré esta propiedad.")
            
            break

        # Genera una pregunta considerando el contexto
        pregunta_aspecto = agente_propiedad.generar_pregunta_natural(proximo)
        print(f"Agente Inmobiliario: {pregunta_aspecto}")

        user_input = input("🧑 Tú: ")
        if user_input.lower() in ["salir", "exit", "adiós"]:
            print("Agente Inmobiliario: ¡Gracias por tu tiempo! Nos vemos pronto.")
            break

        # Guardar la respuesta del usuario en el diccionario
        agente_propiedad.respuestas_usuario[proximo] = user_input

        # Guardar en la memoria de la conversación
        agente_propiedad.memory.save_context({"input": pregunta_aspecto}, {"output": user_input})

if __name__ == "__main__":
    chatear_con_agente() 