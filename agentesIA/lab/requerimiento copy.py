import os
import sys
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
# Importar la herramienta del segundo archivo
import requerimientoTool

# Asegurar codificación UTF-8 para la terminal
sys.stdout.reconfigure(encoding='utf-8')

# Cargar variables de entorno
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Inicializar la memoria de la conversación
memory = ConversationBufferMemory(memory_key="history")

# Inicializar el modelo de lenguaje con GPT-4
llm = ChatOpenAI(model_name="gpt-4", temperature=0.7, openai_api_key=OPENAI_API_KEY)

# Lista de aspectos clave a preguntar
aspectos = [
    "tipo_negocio", "tipo_propiedad", "personas", "mascotas", 
    "presupuesto_min", "presupuesto_max", "area", "habitaciones", 
    "banos", "parqueaderos", "ubicacion", "cercanias", 
    "aspectos_negociables", "aspectos_no_negociables", "fecha_ideal"
]

# Diccionario para almacenar las respuestas del usuario
respuestas_usuario = {aspecto: None for aspecto in aspectos}

def proximo_aspecto():
    """Retorna el primer aspecto sin respuesta o None si todos están completos."""
    for aspecto, respuesta in respuestas_usuario.items():
        if respuesta is None:
            return aspecto
    return None

def generar_pregunta_natural(aspecto):
    """
    Usa el LLM para generar una pregunta natural y conversacional,
    teniendo en cuenta las respuestas previas del usuario.
    """
    historial = memory.load_memory_variables({})["history"]
    respuestas_previas = "\n".join(f"{k}: {v}" for k, v in respuestas_usuario.items() if v)

    prompt_natural = (
        f"Actúa como un agente inmobiliario experto en entender necesidades de clientes. "
        f"Debes hacer preguntas naturales y contextuales para obtener información sobre una propiedad. "
        f"Toma en cuenta la información que el usuario ya proporcionó.\n\n"
        f"Historial de conversación:\n{historial}\n\n"
        f"Respuestas previas del usuario:\n{respuestas_previas}\n\n"
        f"Genera una pregunta NATURAL sobre '{aspecto}', usando el contexto si es relevante."
    )

    pregunta_generada = llm.predict(prompt_natural)
    return pregunta_generada

def generar_resumen():
    """
    Revisa todo el historial de conversación y las respuestas del usuario para generar un resumen
    natural y descriptivo del requerimiento completo.
    """
    # Obtener el historial completo de la conversación
    historial = memory.load_memory_variables({})["history"]
    
    # Compilar las respuestas proporcionadas por el usuario
    respuestas_previas = "\n".join(f"{aspecto}: {respuesta}" 
                                   for aspecto, respuesta in respuestas_usuario.items() 
                                   if respuesta is not None)
    
    # Crear el prompt para que el LLM genere un resumen natural
    prompt_resumen = (
        "Actúa como un agente inmobiliario profesional y elabora un resumen detallado y natural "
        "de toda la información proporcionada por el usuario para encontrar la propiedad ideal. "
        "Debes incluir los detalles clave, resaltar los requerimientos y necesidades expresadas, "
        "y presentar la información de forma clara y descriptiva.\n\n"
        f"Historial de conversación:\n{historial}\n\n"
        f"Respuestas del usuario:\n{respuestas_previas}\n\n"
        "Resumen:"
    )
    
    # Usar el LLM para generar el resumen
    resumen = llm.predict(prompt_resumen)
    return resumen

def chatear_con_agente():
    print("Agente Inmobiliario: ¡Hola! Te ayudaré a encontrar la propiedad ideal.")
    
    while True:
        proximo = proximo_aspecto()
        if proximo is None:
            print("Agente Inmobiliario: Gracias, te enseñaré el resumen de tu requerimiento")
            resumen = generar_resumen()
            print("\nResumen del requerimiento:\n", resumen)
            
            # Preguntar al usuario si el resumen es correcto
            print("\nAgente Inmobiliario: ¿Este resumen es correcto? (sí/no)")
            confirmacion = input("🧑 Tú: ")
            
            if confirmacion.lower() in ["sí", "si", "s", "yes", "y"]:
                print("Agente Inmobiliario: Perfecto, voy a registrar este requerimiento en el sistema...")
                # Usar la función agent_tool del segundo script pasando el resumen
                exito, resultado = requerimientoTool.agent_tool(resumen)
                
                if exito:
                    print("Agente Inmobiliario: ¡El requerimiento ha sido registrado exitosamente!")
                    print(f"ID del requerimiento: {resultado.get('id', 'No disponible')}")
                else:
                    print("Agente Inmobiliario: Lo siento, hubo un problema al registrar el requerimiento.")
                    print(f"Error: {resultado.get('error', 'Desconocido')}")
                    
                print("Agente Inmobiliario: ¡Gracias por tu tiempo!")
            else:
                print("Agente Inmobiliario: Entiendo, ¿deseas modificar algún aspecto de tu requerimiento? (sí/no)")
                modificar = input("🧑 Tú: ")
                if modificar.lower() in ["sí", "si", "s", "yes", "y"]:
                    # Reiniciar aspectos específicos o todos
                    print("Agente Inmobiliario: Por favor indícame qué aspectos deseas modificar (separados por coma) o escribe 'todos' para reiniciar:")
                    aspectos_modificar = input("🧑 Tú: ")
                    if aspectos_modificar.lower() == "todos":
                        # Reiniciar todos los aspectos
                        for aspecto in respuestas_usuario:
                            respuestas_usuario[aspecto] = None
                    else:
                        # Reiniciar solo los aspectos indicados
                        for aspecto in aspectos_modificar.split(","):
                            aspecto = aspecto.strip()
                            if aspecto in respuestas_usuario:
                                respuestas_usuario[aspecto] = None
                    continue  # Volver al inicio del bucle
                else:
                    print("Agente Inmobiliario: Entendido. No registraré este requerimiento.")
            
            break

        # Genera una pregunta considerando el contexto
        pregunta_aspecto = generar_pregunta_natural(proximo)
        print(f"Agente Inmobiliario: {pregunta_aspecto}")

        user_input = input("🧑 Tú: ")
        if user_input.lower() in ["salir", "exit", "adiós"]:
            print("Agente Inmobiliario: ¡Gracias por tu tiempo! Nos vemos pronto.")
            break

        # Guardar la respuesta del usuario en el diccionario
        respuestas_usuario[proximo] = user_input

        # Guardar en la memoria de la conversación
        memory.save_context({"input": pregunta_aspecto}, {"output": user_input})

if __name__ == "__main__":
    chatear_con_agente()
