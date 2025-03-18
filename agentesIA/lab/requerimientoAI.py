import streamlit as st
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import json
import re
import requests

# Cargar variables de entorno
load_dotenv()

# Configurar el modelo de lenguaje
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# Título de la aplicación
st.title("NORA - Asistente Inmobiliario")

# Definir la estructura de información que necesitamos recopilar
CAMPOS_REQUERIMIENTO = [
    {
        "id": "tipo_negocio",
        "nombre": "Tipo de negocio",
        "descripcion": "Si el usuario quiere comprar, arrendar o invertir",
        "pregunta_base": "¿Estás interesado en comprar o arrendar una propiedad?",
        "completado": False,
        "valor": None,
        "obligatorio": True,
        "orden": 1  # Primer campo a preguntar
    },
    {
        "id": "tipo_propiedad",
        "nombre": "Tipo de propiedad",
        "descripcion": "Si el usuario quiere comprar, arrendar o invertir",
        "pregunta_base": "¿Estás interesado en comprar o arrendar una propiedad?",
        "completado": False,
        "valor": None,
        "obligatorio": True,
    },
    {
        "id": "habitantes",
        "nombre": "Habitantes",
        "descripcion": "Número de personas que vivirán en la propiedad",
        "pregunta_base": "¿Cuántas personas vivirán en la propiedad?",
        "completado": False,
        "valor": None,
        "obligatorio": True,
        "orden": 2  # Segundo campo a preguntar
    },
    {
        "id": "mascotas",
        "nombre": "Mascotas",
        "descripcion": "Si tiene mascotas que vivirán en la propiedad",
        "pregunta_base": "¿Tienes mascotas que vivirán en la propiedad?",
        "completado": False,
        "valor": None,
        "obligatorio": True,
        "orden": 3  # Tercer campo a preguntar
    },
    {
        "id": "tiempo_estadia",
        "nombre": "Tiempo de estadía",
        "descripcion": "Por cuánto tiempo planea arrendar (solo para arriendo)",
        "pregunta_base": "¿Por cuánto tiempo planeas arrendar la propiedad?",
        "completado": False,
        "valor": None,
        "obligatorio": False,  # Solo obligatorio para arriendo
        "condicion": lambda campos: campos["tipo_negocio"]["valor"] == "arriendo"
    },
    {
        "id": "presupuesto",
        "nombre": "Presupuesto",
        "descripcion": "Rango de presupuesto para la propiedad",
        "pregunta_base": "¿Cuál es tu presupuesto para esta propiedad?",
        "completado": False,
        "valor": None,
        "obligatorio": True
    },
    {
        "id": "ubicacion",
        "nombre": "Ubicación",
        "descripcion": "Zona, barrio o sector deseado",
        "pregunta_base": "¿En qué zona o barrio te gustaría que esté ubicada la propiedad?",
        "completado": False,
        "valor": None,
        "obligatorio": True
    },
    {
        "id": "habitaciones",
        "nombre": "Habitaciones",
        "descripcion": "Número de habitaciones necesarias",
        "pregunta_base": "¿Cuántas habitaciones necesitas en la propiedad?",
        "completado": False,
        "valor": None,
        "obligatorio": True
    },
    {
        "id": "banos",
        "nombre": "Baños",
        "descripcion": "Número de baños necesarios",
        "pregunta_base": "¿Cuántos baños necesitas en la propiedad?",
        "completado": False,
        "valor": None,
        "obligatorio": True
    },
    {
        "id": "area",
        "nombre": "Área",
        "descripcion": "Tamaño aproximado en metros cuadrados",
        "pregunta_base": "¿Qué tamaño aproximado en metros cuadrados estás buscando?",
        "completado": False,
        "valor": None,
        "obligatorio": True
    },
    {
        "id": "parqueaderos",
        "nombre": "Parqueaderos",
        "descripcion": "Número de parqueaderos necesarios",
        "pregunta_base": "¿Necesitas parqueadero? ¿Para cuántos vehículos?",
        "completado": False,
        "valor": None,
        "obligatorio": True
    },
    {
        "id": "negociables",
        "nombre": "Aspectos negociables",
        "descripcion": "Características sobre las que el usuario podría ceder",
        "pregunta_base": "¿Hay aspectos o características sobre las que podrías ser flexible o negociar?",
        "completado": False,
        "valor": None,
        "obligatorio": True
    },
    {
        "id": "no_negociables",
        "nombre": "Aspectos no negociables",
        "descripcion": "Características indispensables para el usuario",
        "pregunta_base": "¿Qué características o aspectos son indispensables para ti en esta propiedad?",
        "completado": False,
        "valor": None,
        "obligatorio": True
    },
    {
        "id": "caracteristicas_especiales",
        "nombre": "Características especiales",
        "descripcion": "Características adicionales deseadas",
        "pregunta_base": "¿Hay alguna característica especial que te gustaría que tuviera la propiedad?",
        "completado": False,
        "valor": None,
        "obligatorio": True
    }
]

# Constantes para la API
API_URL = "http://localhost:8000/requerimientos/"
AGENTE_ID = 12
CLIENTE_ID = 29

# Inicializar el estado de la sesión
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "conversation_complete" not in st.session_state:
    st.session_state.conversation_complete = False
    
if "requerimiento" not in st.session_state:
    st.session_state.requerimiento = None

if "campos_requerimiento" not in st.session_state:
    st.session_state.campos_requerimiento = CAMPOS_REQUERIMIENTO

if "pregunta_actual" not in st.session_state:
    st.session_state.pregunta_actual = "tipo_negocio"

if "debug_logs" not in st.session_state:
    st.session_state.debug_logs = []

if "revision_pendiente" not in st.session_state:
    st.session_state.revision_pendiente = False

if "contador_interacciones" not in st.session_state:
    st.session_state.contador_interacciones = 0

# Función para agregar logs de depuración
def log_debug(mensaje):
    print(f"[DEBUG] {mensaje}")
    st.session_state.debug_logs.append(mensaje)

# Mensaje inicial del asistente
if not st.session_state.messages:
    mensaje_inicial = (
        "Hola, soy NORA, tu asistente inmobiliaria. Estoy aquí para ayudarte a encontrar "
        "la propiedad perfecta para ti."
        "¿Te interesa comprar o buscas un lugar para rentar?"
    )
    st.session_state.messages.append({"role": "assistant", "content": mensaje_inicial})
    log_debug("Iniciando conversación con mensaje de bienvenida")

# Mostrar mensajes anteriores
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Función mejorada para evaluar si la respuesta del usuario satisface la pregunta actual
def evaluar_respuesta(respuesta_usuario, pregunta_id, pregunta_texto):
    log_debug(f"Evaluando respuesta para pregunta '{pregunta_id}': '{respuesta_usuario}'")
    
    # Instrucciones específicas según el tipo de campo
    instrucciones_especificas = {
        "habitaciones": "Para habitaciones, extrae SOLO un número entero (1, 2, 3, etc.). Si el usuario menciona 'una habitación adicional' o similar, deduce el número total.",
        "banos": "Para baños, extrae SOLO un número entero (1, 2, 3, etc.).",
        "parqueaderos": "Para parqueaderos, extrae SOLO un número entero (0, 1, 2, etc.). Si el usuario dice que no necesita o no tiene vehículo, el valor debe ser 0.",
        "area": "Para área, extrae SOLO un número que represente metros cuadrados.",
        "presupuesto": "Para presupuesto, extrae el valor numérico y asegúrate de convertirlo a una cifra estándar.",
        "negociables": "Acepta respuestas como 'no' o 'ninguno' como válidas si el usuario no tiene aspectos negociables."
    }
    
    instruccion_campo = instrucciones_especificas.get(pregunta_id, "")
    
    # Preparar el mensaje para el modelo
    system_prompt = f"""
    Eres un asistente especializado en analizar conversaciones inmobiliarias con extrema precisión.
    
    Evalúa si la respuesta del usuario proporciona la información solicitada en la pregunta.
    
    Pregunta: {pregunta_texto}
    Respuesta: {respuesta_usuario}
    
    IMPORTANTE: 
    1. Sé extremadamente preciso al extraer la información relevante.
    2. {instruccion_campo}
    3. No incluyas información de otros campos en el valor extraído.
    4. Si la pregunta pide un número, el valor extraído DEBE ser un número.
    5. Para respuestas como "no tengo vehículo" a la pregunta sobre parqueaderos, el valor debe ser 0.
    6. Para 'negociables', acepta 'no' o 'ninguno' como respuestas válidas si no hay aspectos negociables.
    
    Debes determinar:
    1. Si la respuesta proporciona la información solicitada (SATISFACE o NO_SATISFACE)
    2. Qué valor específico proporciona el usuario (número o texto simple, sin elaboración)
    3. Tu nivel de confianza en esta evaluación (ALTA, MEDIA, BAJA)
    
    Responde en formato JSON con los siguientes campos:
    {{
        "satisface": "SATISFACE" o "NO_SATISFACE",
        "valor_extraido": el valor específico extraído (número puro o texto simple),
        "explicacion": breve explicación de tu evaluación,
        "confianza": "ALTA", "MEDIA", o "BAJA"
    }}
    """
    
    # Convertir al formato que espera el modelo
    messages = [
        ["system", system_prompt],
        ["human", "Evalúa esta respuesta."]
    ]
    
    # Obtener la respuesta del modelo
    response = llm.invoke(messages).content
    log_debug(f"Respuesta del modelo para evaluación: {response}")
    
    # Intentar parsear el JSON
    try:
        # Extraer solo el JSON si hay texto adicional
        json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
        if json_match:
            response = json_match.group(1)
        
        # Limpiar posibles caracteres no deseados
        response = response.strip()
        if response.startswith('```') and response.endswith('```'):
            response = response[3:-3].strip()
        
        evaluacion = json.loads(response)
        
        # Normalizar valores para campos numéricos
        if pregunta_id in ["habitaciones", "banos", "parqueaderos", "area"]:
            try:
                # Si el valor extraído es un texto que contiene un número, extraer solo el número
                if isinstance(evaluacion["valor_extraido"], str):
                    match = re.search(r'(\d+)', evaluacion["valor_extraido"])
                    if match:
                        evaluacion["valor_extraido"] = int(match.group(1))
                # Convertir a entero si es posible
                if evaluacion["valor_extraido"] is not None:
                    evaluacion["valor_extraido"] = int(float(evaluacion["valor_extraido"]))
            except (ValueError, TypeError):
                log_debug(f"No se pudo convertir a número el valor: {evaluacion['valor_extraido']}")
                # Si hay un problema con la conversión, usar un valor por defecto según el campo
                defaults = {"habitaciones": 2, "banos": 1, "parqueaderos": 0, "area": 60}
                evaluacion["valor_extraido"] = defaults.get(pregunta_id, None)
                evaluacion["confianza"] = "BAJA"
        
        # Aceptar respuestas negativas para 'negociables'
        if pregunta_id == "negociables" and evaluacion["valor_extraido"].lower() in ["no", "ninguno"]:
            evaluacion["satisface"] = "SATISFACE"
            evaluacion["confianza"] = "ALTA"
        
        log_debug(f"Evaluación parseada y normalizada: {evaluacion}")
        return evaluacion
    except Exception as e:
        log_debug(f"Error al parsear evaluación: {str(e)}")
        # Fallback: intentar extraer los campos manualmente
        satisface = "SATISFACE" if "SATISFACE" in response.upper() and "NO_SATISFACE" not in response.upper() else "NO_SATISFACE"
        return {
            "satisface": satisface,
            "valor_extraido": None,
            "explicacion": "Error al parsear la respuesta",
            "confianza": "BAJA"
        }

# Función para ofrecer ayuda proactiva cuando el usuario está confundido
def generar_ayuda_proactiva(campo_id):
    campo = obtener_campo(campo_id)
    
    # Ejemplos de respuestas según el tipo de campo
    ejemplos = {
        "tipo_negocio": "Por ejemplo, puedes decir 'Quiero comprar' o 'Estoy interesado en arrendar'.",
        "tipo_propiedad": "Por ejemplo, puedes decir 'Quiero una casa' o 'Me interesa un apartamento'",
        "habitantes": "Por ejemplo, puedes decir '2 personas', 'Somos 3 en la familia', etc.",
        "mascotas": "Por ejemplo, 'Tengo un perro', 'No tengo mascotas', etc.",
        "presupuesto": "Por ejemplo, '200 millones', 'Entre 1 y 2 millones mensuales', etc.",
        "ubicacion": "Por ejemplo, 'Me gustaría en el norte de la ciudad', 'Preferiblemente en Laureles', etc.",
        "habitaciones": "Por ejemplo, '3 habitaciones', '2 alcobas', etc.",
        "banos": "Por ejemplo, '2 baños', 'Al menos 1 baño completo', etc.",
        "area": "Por ejemplo, '80 metros cuadrados', 'Entre 100 y 120 m2', etc.",
        "parqueaderos": "Por ejemplo, 'Necesito 1 parqueadero', 'No necesito parqueadero', etc.",
        "negociables": "Por ejemplo, 'Podría ceder en el tamaño del patio', 'El número de parqueaderos es negociable', etc.",
        "no_negociables": "Por ejemplo, 'Debe tener buena iluminación', 'Es indispensable que tenga terraza', etc."
    }
    
    ayuda = f"Entiendo que quizás mi pregunta no fue clara. {ejemplos.get(campo_id, 'Por favor, proporciona la información solicitada.')} ¿Te parece bien?"
    
    return ayuda

# Función para generar la siguiente pregunta con orden específico
def generar_siguiente_pregunta():
    log_debug("Determinando la siguiente pregunta a hacer")
    
    # Obtener todos los campos
    campos = st.session_state.campos_requerimiento
    
    # Primero verificar si hay campos con orden específico pendientes
    for orden in [1, 2, 3]:  # Orden fijo para las primeras preguntas
        for campo in campos:
            if campo.get("orden") == orden and not campo["completado"]:
                log_debug(f"Siguiente pregunta por orden específico: {campo['id']}")
                return campo["id"]
    
    # Verificar si hay campos obligatorios pendientes
    for campo in campos:
        # Verificar si el campo es obligatorio y no está completado
        es_obligatorio = campo["obligatorio"]
        
        # Si el campo tiene una condición, evaluarla
        if "condicion" in campo:
            es_obligatorio = es_obligatorio and campo["condicion"](
                {c["id"]: {"valor": c["valor"]} for c in campos}
            )
        
        if es_obligatorio and not campo["completado"] and not campo.get("orden") in [1, 2, 3]:
            log_debug(f"Siguiente pregunta: {campo['id']}")
            return campo["id"]
    
    # Si todos los campos obligatorios están completados, la conversación está completa
    log_debug("Todos los campos obligatorios están completados")
    return None

# Función para obtener el campo actual por ID
def obtener_campo(campo_id):
    for campo in st.session_state.campos_requerimiento:
        if campo["id"] == campo_id:
            return campo
    return None

# Función para actualizar un campo
def actualizar_campo(campo_id, completado=None, valor=None):
    for i, campo in enumerate(st.session_state.campos_requerimiento):
        if campo["id"] == campo_id:
            if completado is not None:
                st.session_state.campos_requerimiento[i]["completado"] = completado
            if valor is not None:
                st.session_state.campos_requerimiento[i]["valor"] = valor
            log_debug(f"Campo actualizado: {campo_id}, completado: {completado}, valor: {valor}")
            return True
    return False

# Función para formular la pregunta de manera natural
def formular_pregunta(campo_id, historial):
    campo = obtener_campo(campo_id)
    if not campo:
        log_debug(f"Error: No se encontró el campo {campo_id}")
        return "¿Hay algo más que quieras contarme sobre lo que buscas?"
    
    log_debug(f"Formulando pregunta para campo: {campo_id}")
    
    # Preparar el mensaje para el modelo
    system_prompt = f"""
    Eres NORA, una asistente inmobiliaria profesional y amigable.
    
    Necesito que formules una pregunta natural y conversacional para obtener información sobre: {campo['nombre']}.
    
    La pregunta base es: "{campo['pregunta_base']}"
    
    Pero quiero que la adaptes para que:
    1. Suene natural y amigable, no como un cuestionario
    2. Se conecte con lo que ya se ha hablado en la conversación
    3. Sea una sola pregunta clara y específica
    4. No repita información que ya se ha proporcionado
    
    Responde ÚNICAMENTE con la pregunta formulada, sin explicaciones adicionales.
    """
    
    # Convertir el historial al formato que espera el modelo
    messages = [
        ["system", system_prompt],
        ["human", "Aquí está la conversación hasta ahora:\n\n" + "\n\n".join([f"{m['role']}: {m['content']}" for m in historial])]
    ]
    
    # Obtener la respuesta del modelo
    response = llm.invoke(messages).content
    log_debug(f"Pregunta formulada: {response}")
    
    return response

# Nueva función para normalizar valores antes del resumen final
def normalizar_valores_requerimiento():
    log_debug("Normalizando valores del requerimiento antes del resumen final")
    
    # Obtener todos los campos
    campos = st.session_state.campos_requerimiento
    
    # Lista de campos que deberían tener valores numéricos
    campos_numericos = ["habitaciones", "banos", "parqueaderos", "area"]
    
    # Normalizar campos
    for campo in campos:
        if campo["id"] in campos_numericos and campo["completado"]:
            try:
                # Si el valor es una cadena que contiene un número, extraer solo el número
                if isinstance(campo["valor"], str):
                    match = re.search(r'(\d+)', campo["valor"])
                    if match:
                        campo["valor"] = int(match.group(1))
                        log_debug(f"Valor normalizado para {campo['id']}: {campo['valor']}")
                    else:
                        # Si no se encuentra un número en la cadena, usar un valor por defecto
                        defaults = {"habitaciones": 2, "banos": 1, "parqueaderos": 0, "area": 60}
                        campo["valor"] = defaults.get(campo["id"], 0)
                        log_debug(f"Valor normalizado (por defecto) para {campo['id']}: {campo['valor']}")
            except Exception as e:
                log_debug(f"Error al normalizar el valor para {campo['id']}: {str(e)}")
    
    # Si parqueaderos está completado y el valor indica que no se necesitan, asegurar que sea 0
    parqueaderos = next((c for c in campos if c["id"] == "parqueaderos"), None)
    if parqueaderos and parqueaderos["completado"]:
        valor = parqueaderos["valor"]
        if valor is None or (isinstance(valor, str) and "no" in valor.lower()):
            parqueaderos["valor"] = 0
            log_debug("Valor de parqueaderos establecido a 0 basado en la respuesta negativa")

# Modificar la función para analizar conversación completa
def analizar_conversacion_completa():
    log_debug("Analizando la conversación completa para extraer información adicional")
    
    # Preparar el mensaje para el modelo
    system_prompt = """
    Eres un asistente especializado en analizar conversaciones inmobiliarias con extrema precisión.
    
    Revisa cuidadosamente la siguiente conversación entre un usuario y un asistente inmobiliario.
    Busca cualquier información relevante que pueda haberse mencionado pero no se haya registrado explícitamente.
    
    IMPORTANTE:
    1. Para campos numéricos (habitaciones, baños, parqueaderos, área), extrae SOLO el número.
    2. Si el usuario dice que no tiene vehículo o no necesita parqueadero, el valor de parqueaderos debe ser 0.
    3. Sé muy específico y preciso, evitando mezclar información entre campos diferentes.
    
    Responde en formato JSON con la información encontrada, usando null para campos sin información:
    {
        "tipo_negocio": valor extraído o null,
        "tipo_propiedad": valor extraído o null,
        "habitantes": valor numérico o null,
        "mascotas": "si"/"no" o descripción simple,
        "presupuesto": valor numérico o null,
        "ubicacion": ubicación específica o null,
        "habitaciones": número entero o null,
        "banos": número entero o null,
        "area": número entero o null,
        "parqueaderos": número entero o null,
        "negociables": descripción simple o null,
        "no_negociables": descripción simple o null,
        "caracteristicas_especiales": descripción simple o null
    }
    """
    
    # Convertir el historial al formato que espera el modelo
    messages = [
        ["system", system_prompt],
        ["human", "Aquí está la conversación:\n\n" + "\n\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])]
    ]
    
    # Obtener la respuesta del modelo
    response = llm.invoke(messages).content
    log_debug(f"Resultado del análisis completo: {response[:100]}...")
    
    try:
        # Extraer solo el JSON si hay texto adicional
        json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
        if json_match:
            response = json_match.group(1)
        
        # Limpiar posibles caracteres no deseados
        response = response.strip()
        if response.startswith('```') and response.endswith('```'):
            response = response[3:-3].strip()
        
        analisis = json.loads(response)
        
        # Normalizar valores numéricos
        campos_numericos = ["habitaciones", "banos", "parqueaderos", "area", "habitantes"]
        for campo in campos_numericos:
            if campo in analisis and analisis[campo] is not None:
                try:
                    if isinstance(analisis[campo], str):
                        match = re.search(r'(\d+)', analisis[campo])
                        if match:
                            analisis[campo] = int(match.group(1))
                except Exception as e:
                    log_debug(f"Error al normalizar el valor para {campo} en análisis completo: {str(e)}")
        
        # Actualizar campos con información encontrada
        campos_actualizados = 0
        for campo_id, valor in analisis.items():
            campo = obtener_campo(campo_id)
            if campo and not campo["completado"] and valor is not None:
                actualizar_campo(campo_id, completado=True, valor=valor)
                campos_actualizados += 1
                log_debug(f"Campo actualizado por análisis completo: {campo_id} = {valor}")
        
        log_debug(f"Análisis completo actualizó {campos_actualizados} campos")
        return campos_actualizados > 0
    except Exception as e:
        log_debug(f"Error en análisis completo: {str(e)}")
        return False

# Modificar la parte donde se extrae el requerimiento final
def extraer_requerimiento_final():
    log_debug("Extrayendo requerimiento final")
    
    # Realizar un análisis final de la conversación
    analizar_conversacion_completa()
    
    # Normalizar los valores antes de generar el requerimiento
    normalizar_valores_requerimiento()
    
    # Crear el requerimiento a partir de los campos completados
    requerimiento = {}
    
    for campo in st.session_state.campos_requerimiento:
        if campo["completado"]:
            requerimiento[campo["id"]] = campo["valor"]
        else:
            requerimiento[campo["id"]] = None
    
    # Agregar campos adicionales
    requerimiento["estado"] = "pendiente"
    requerimiento["prioridad"] = "normal"
    requerimiento["descripcion"] = "\n".join([m["content"] for m in st.session_state.messages if m["role"] == "user"])
    
    log_debug(f"Requerimiento final: {requerimiento}")
    return requerimiento

# Modificar la función para generar un resumen en lenguaje natural dirigido al usuario
def generar_resumen_natural():
    log_debug("Generando resumen en lenguaje natural")
    
    # Preparar los datos para el resumen
    datos = {}
    for campo in st.session_state.campos_requerimiento:
        if campo["completado"] and campo["valor"] is not None:
            datos[campo["id"]] = {
                "nombre": campo["nombre"],
                "valor": campo["valor"]
            }
    
    # Modificar el system prompt para dirigirse directamente al usuario
    system_prompt = """
    Eres NORA, un asistente inmobiliario profesional que está hablando directamente con un cliente.
    
    Genera un resumen en lenguaje natural y conversacional de los requisitos inmobiliarios que has
    recopilado durante tu conversación con el cliente.
    
    El resumen debe estar escrito en SEGUNDA PERSONA, dirigiéndote directamente al cliente, usando "tú"
    en lugar de hablar de "el cliente" o "el usuario".
    
    Usa un tono profesional pero amigable, y asegúrate de incluir todos los detalles proporcionados.
    No uses formato de lista, sino párrafos fluidos y naturales.
    
    Comienza con una frase como "Basado en nuestra conversación, entiendo que estás buscando..." y
    continúa describiendo todos los detalles de manera coherente y organizada utilizando siempre
    formulaciones como "tú estás buscando", "tú necesitas", "tú prefieres", etc.
    
    No menciones "el cliente" o "el usuario" en ningún momento.
    """
    
    # Convertir al formato que espera el modelo
    messages = [
        ["system", system_prompt],
        ["human", f"Aquí están los datos del requerimiento: {json.dumps(datos, ensure_ascii=False)}"]
    ]
    
    # Obtener la respuesta del modelo
    response = llm.invoke(messages).content
    log_debug(f"Resumen generado: {response}")
    
    return response

# Función para solicitar validación del usuario de manera explícita
def solicitar_validacion_resumen(resumen):
    log_debug("Solicitando validación del resumen al usuario")
    
    # Crear un mensaje que muestre el resumen y solicite validación de forma clara
    mensaje_validacion = f"""
¡Perfecto! Ya tengo toda la información necesaria para ayudarte a encontrar la propiedad ideal. Basado en nuestra conversación, este es el requerimiento que he preparado:

{resumen}

**¿CONFIRMAS QUE PODEMOS REGISTRAR ESTE REQUERIMIENTO?** 
Por favor responde "SÍ" para registrar el requerimiento o "NO" si deseas hacer cambios.
"""
    
    return mensaje_validacion

# Función para evaluar si el usuario ha validado el resumen
def evaluate_validation_response(user_message):
    log_debug(f"Evaluando respuesta de validación: {user_message}")
    
    # Patrones para respuestas positivas - más específicos y claros
    patrones_positivos = [
        'sí', 'si', 'confirmo', 'confirmar', 'apruebo', 'aprobar', 'acepto', 'aceptar',
        'está correcto', 'correcto', 'adelante', 'procede', 'proceder', 'registrar'
    ]
    
    # Verificar si el mensaje contiene alguno de los patrones positivos
    user_message_lower = user_message.lower()
    es_validacion_positiva = any(patron in user_message_lower for patron in patrones_positivos)
    
    # Si no contiene negaciones que invaliden la respuesta positiva
    if es_validacion_positiva:
        negaciones = ['no ', 'no está', 'no es', 'no me', 'incorrecto', 'mal', 'error']
        for negacion in negaciones:
            if negacion in user_message_lower:
                es_validacion_positiva = False
                break
    
    log_debug(f"Resultado de evaluación: es_validacion_positiva={es_validacion_positiva}")
    
    return {
        'es_validacion_positiva': es_validacion_positiva,
        'mensaje_original': user_message
    }

# Función para crear el requerimiento final y enviarlo a la API
def crear_requerimiento_final():
    log_debug("Creando requerimiento final")
    
    # Preparar los datos para enviar a la API
    datos_requerimiento = {}
    
    # Agregar IDs fijos
    datos_requerimiento['agente'] = AGENTE_ID
    datos_requerimiento['cliente'] = CLIENTE_ID
    
    # Mapear los campos del estado de la sesión al formato que espera la API
    for campo in st.session_state.campos_requerimiento:
        if campo["completado"] and campo["valor"] is not None:
            campo_id = campo["id"]
            campo_valor = campo["valor"]
            
            log_debug(f"Procesando campo {campo_id} con valor {campo_valor}")
            
            # Mapeo de campos según el modelo RequerimientoModel
            if campo_id == "tipo_negocio":
                datos_requerimiento['tipo_negocio'] = json.dumps({"tipo": campo_valor})
            elif campo_id == "habitantes":
                datos_requerimiento['habitantes'] = int(campo_valor)
            elif campo_id == "mascotas":
                datos_requerimiento['mascotas'] = "si" if campo_valor else "no"
            elif campo_id == "presupuesto":
                # Determinar si es compra o renta para asignar el presupuesto correctamente
                tipo_negocio = next((c["valor"] for c in st.session_state.campos_requerimiento if c["id"] == "tipo_negocio"), None)
                if tipo_negocio == "compra":
                    datos_requerimiento['presupuesto_minimo_compra'] = float(campo_valor) * 0.9
                    datos_requerimiento['presupuesto_maximo_compra'] = float(campo_valor)
                else:  # renta
                    datos_requerimiento['presupuesto_minimo'] = float(campo_valor) * 0.9
                    datos_requerimiento['presupuesto_maximo'] = float(campo_valor)
            elif campo_id == "ubicacion" or campo_id == "zona":
                # Guardar la ubicación en la descripción
                if "descripcion" not in datos_requerimiento:
                    datos_requerimiento['descripcion'] = ""
                datos_requerimiento['descripcion'] += f"Ubicación: {campo_valor}. "
            elif campo_id == "habitaciones":
                datos_requerimiento['habitaciones'] = int(campo_valor)
            elif campo_id == "banos":
                datos_requerimiento['banos'] = int(campo_valor)
            elif campo_id == "area":
                datos_requerimiento['area_minima'] = int(campo_valor)
            elif campo_id == "parqueaderos":
                datos_requerimiento['parqueaderos'] = int(campo_valor)
            elif campo_id == "negociables":
                datos_requerimiento['negocibles'] = campo_valor
            elif campo_id == "no_negociables":
                datos_requerimiento['no_negocibles'] = campo_valor
            elif campo_id == "tiempo_estadia" and campo_valor:
                datos_requerimiento['tiempo_estadia'] = int(campo_valor)
            elif campo_id == "tipo_propiedad":
                # Añadir tipo de propiedad a la descripción
                if "descripcion" not in datos_requerimiento:
                    datos_requerimiento['descripcion'] = ""
                datos_requerimiento['descripcion'] += f"Tipo de propiedad: {campo_valor}. "
            elif campo_id == "caracteristicas_especiales":
                # Añadir características especiales a la descripción
                if "descripcion" not in datos_requerimiento:
                    datos_requerimiento['descripcion'] = ""
                datos_requerimiento['descripcion'] += f"Características especiales: {campo_valor}. "
    
    # Asegurarse de que todos los campos requeridos estén presentes
    if "descripcion" not in datos_requerimiento:
        datos_requerimiento['descripcion'] = "Requerimiento generado por NORA."
    
    # Valores por defecto para campos obligatorios que podrían faltar
    if "tipo_negocio" not in datos_requerimiento:
        datos_requerimiento['tipo_negocio'] = json.dumps({"tipo": "no especificado"})
    
    log_debug(f"Datos del requerimiento preparados: {datos_requerimiento}")
    
    try:
        # Realizar la llamada a la API
        log_debug(f"Enviando solicitud POST a {API_URL}")
        response = requests.post(API_URL, json=datos_requerimiento)
        
        # Verificar si la llamada fue exitosa
        if response.status_code == 201:  # HTTP 201 Created
            log_debug(f"Requerimiento creado exitosamente en la API. Respuesta: {response.text}")
            st.session_state['requerimiento_creado'] = True
            st.session_state['requerimiento_id'] = response.json().get('id')
            return True
        else:
            log_debug(f"Error al crear requerimiento: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        log_debug(f"Excepción al crear requerimiento: {str(e)}")
        return False

# Procesar la entrada del usuario
if prompt := st.chat_input("Escribe tu mensaje..."):
    # Agregar el mensaje del usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    log_debug(f"Mensaje del usuario recibido: {prompt}")
    
    # Mostrar el mensaje del usuario
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Incrementar contador de interacciones
    st.session_state.contador_interacciones += 1
    
    # Si la conversación no está completa, procesar la respuesta
    if not st.session_state.conversation_complete:
        with st.spinner("NORA está pensando..."):
            # Verificar si es momento de hacer una revisión completa (cada 5 interacciones)
            if st.session_state.contador_interacciones % 5 == 0:
                log_debug("Realizando revisión periódica de la conversación")
                analizar_conversacion_completa()
            
            # Obtener la pregunta actual
            pregunta_actual_id = st.session_state.pregunta_actual
            campo_actual = obtener_campo(pregunta_actual_id)
            
            if campo_actual:
                # Obtener el último mensaje del asistente (la pregunta)
                ultimo_mensaje_asistente = next((m["content"] for m in reversed(st.session_state.messages[:-1]) if m["role"] == "assistant"), "")
                
                # Evaluar si la respuesta satisface la pregunta
                evaluacion = evaluar_respuesta(prompt, pregunta_actual_id, ultimo_mensaje_asistente)
                
                if evaluacion["satisface"] == "SATISFACE":
                    # Marcar la pregunta como completada
                    actualizar_campo(pregunta_actual_id, completado=True, valor=evaluacion["valor_extraido"])
                    
                    # Si es tipo_negocio y el valor es "arriendo", actualizar la obligatoriedad de tiempo_estadia
                    if pregunta_actual_id == "tipo_negocio" and evaluacion["valor_extraido"] == "arriendo":
                        log_debug("Usuario ha indicado arriendo, tiempo_estadia ahora es obligatorio")
                    
                    # Determinar la siguiente pregunta
                    siguiente_pregunta_id = generar_siguiente_pregunta()
                    
                    if siguiente_pregunta_id:
                        # Actualizar la pregunta actual
                        st.session_state.pregunta_actual = siguiente_pregunta_id
                        
                        # Generar la siguiente pregunta
                        respuesta = formular_pregunta(siguiente_pregunta_id, st.session_state.messages)
                    else:
                        # Todas las preguntas han sido respondidas
                        log_debug("Todas las preguntas han sido respondidas")
                        st.session_state.conversation_complete = True
                        
                        # Extraer el requerimiento final
                        st.session_state.requerimiento = extraer_requerimiento_final()
                        
                        # Generar un resumen en lenguaje natural
                        resumen = generar_resumen_natural()
                        
                        # Mensaje de confirmación con el resumen
                        respuesta = (
                            "¡Perfecto! Ya tengo toda la información necesaria para ayudarte a encontrar "
                            "la propiedad ideal. Basado en nuestra conversación, este es el requerimiento que he registrado:\n\n"
                            f"{resumen}\n\n"
                            "¿Hay algo que quieras modificar o agregar a este requerimiento?"
                        )
                elif evaluacion["confianza"] == "BAJA":
                    # Si la confianza es baja, ofrecer ayuda proactiva
                    log_debug(f"Baja confianza en la evaluación. Ofreciendo ayuda proactiva.")
                    respuesta = generar_ayuda_proactiva(pregunta_actual_id)
                else:
                    # La respuesta no satisface la pregunta, reformularla
                    log_debug(f"La respuesta no satisface la pregunta. Explicación: {evaluacion['explicacion']}")
                    
                    # Reformular la pregunta de manera más clara
                    respuesta = (
                        f"{formular_pregunta(pregunta_actual_id, st.session_state.messages)}"
                    )
            else:
                # Error: no se encontró la pregunta actual
                log_debug(f"Error: No se encontró la pregunta actual {pregunta_actual_id}")
                respuesta = "Disculpa, parece que hubo un error. ¿Podrías decirme qué tipo de propiedad estás buscando?"
                st.session_state.pregunta_actual = "tipo_negocio"
    else:
        # Si la conversación ya está completa, responder de forma general
        log_debug("Conversación ya completa. Respondiendo de forma general.")
        respuesta = (
            "Gracias por la información adicional. Ya he registrado tu requerimiento principal, "
            "pero añadiré este detalle a tus comentarios. ¿Hay algo más en lo que pueda ayudarte?"
        )
    
    # Agregar la respuesta al historial
    st.session_state.messages.append({"role": "assistant", "content": respuesta})
    log_debug(f"Respuesta del asistente: {respuesta}")
    
    # Mostrar la respuesta
    with st.chat_message("assistant"):
        st.markdown(respuesta)

# Mostrar el requerimiento extraído en la barra lateral
with st.sidebar:
    st.subheader("Información del Requerimiento")
    
    # Mostrar el progreso de la conversación
    campos = st.session_state.campos_requerimiento
    campos_obligatorios = [c for c in campos if c["obligatorio"]]
    campos_completados = [c for c in campos_obligatorios if c["completado"]]
    
    if campos_obligatorios:
        progreso = len(campos_completados) / len(campos_obligatorios)
        st.progress(progreso)
        st.write(f"**Progreso:** {len(campos_completados)} de {len(campos_obligatorios)} campos completados")
    
    # Mostrar los campos completados
    st.write("**Información recopilada:**")
    for campo in campos:
        if campo["completado"] and campo["valor"] is not None:
            st.write(f"**{campo['nombre']}:** {campo['valor']}")
    
    # Opción para analizar toda la conversación
    if st.button("Revisar conversación"):
        with st.spinner("Analizando la conversación..."):
            cambios_realizados = analizar_conversacion_completa()
            if cambios_realizados:
                st.success("¡Se ha encontrado y actualizado información adicional!")
            else:
                st.info("No se encontró información adicional.")
    
    # Mostrar el requerimiento final si la conversación está completa
    if st.session_state.conversation_complete and st.session_state.requerimiento:
        st.write("---")
        st.write("**Requerimiento completo:**")
        
        # Mostrar el requerimiento extraído
        for key, value in st.session_state.requerimiento.items():
            if value is not None and key != "descripcion":
                st.write(f"**{key.replace('_', ' ').title()}:** {value}")
        
        # Botón para reiniciar la conversación
        if st.button("Nuevo Requerimiento"):
            st.session_state.messages = []
            st.session_state.conversation_complete = False
            st.session_state.requerimiento = None
            st.session_state.campos_requerimiento = CAMPOS_REQUERIMIENTO
            st.session_state.pregunta_actual = "tipo_negocio"
            st.session_state.debug_logs = []
            st.session_state.contador_interacciones = 0
            log_debug("Conversación reiniciada")
            st.rerun()
    
    # Sección de depuración
    st.write("---")
    st.subheader("Información de Depuración")
    if st.checkbox("Mostrar logs de depuración"):
        for i, log in enumerate(st.session_state.debug_logs):
            st.text(f"{i+1}. {log}")
