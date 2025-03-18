import streamlit as st
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import re
import json
import time

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)  # Aumentamos la temperatura para respuestas más naturales

st.title("Chat con NORA")

# Inicializar el requerimiento en el estado de la sesión si no existe
if "requerimiento_data" not in st.session_state:
    st.session_state.requerimiento_data = {
        "tipo_negocio": {},
        "tiempo_estadia": None,
        "presupuesto_minimo_compra": None,
        "presupuesto_maximo_compra": None,
        "presupuesto_minimo_renta": None,
        "presupuesto_maximo_renta": None,
        "habitantes": 0,
        "mascotas": "no",
        "area_minima": None,
        "area_maxima": None,
        "habitaciones": 0,
        "banos": 0,
        "parqueaderos": 0,
        "barrio": None,
        "cercanias": None,
        "negociables": None,
        "no_negociables": None,
        "descripcion": "",
        "fecha_ideal_entrega": None,
        "comentarios": None,
        "estado": "pendiente",
        "prioridad": "normal"
    }

# Inicializar el historial de mensajes de LangChain si no existe
if "langchain_messages" not in st.session_state:
    st.session_state.langchain_messages = [
        {"role": "system", "content": """
        Eres NORA, una asistente inmobiliaria profesional especializada en el mercado inmobiliario. 
        
        INSTRUCCIONES IMPORTANTES:
        1. Haz SOLO UNA PREGUNTA a la vez. Nunca hagas múltiples preguntas en un mismo mensaje.
        2. Mantén un tono conversacional y amigable, como si fueras una persona real.
        3. Evita que tus preguntas suenen como un cuestionario formal.
        4. Recuerda toda la información que el usuario ya ha proporcionado.
        5. Adapta tus siguientes preguntas basándote en lo que ya sabes.
        6. Sé paciente y no apresures al usuario a dar toda la información de una vez.
        
        Tu objetivo es recopilar gradualmente la siguiente información a través de una conversación natural:
        - Tipo de negocio (compra, arriendo, inversión)
        - Si es arriendo, preguntar por el tiempo de estadía
        - Presupuesto (mínimo y máximo)
        - Ubicación deseada (barrio, zona)
        - Número de habitaciones y baños necesarios
        - Área deseada (metros cuadrados)
        - Número de habitantes o personas que vivirán allí
        - Si tienen mascotas
        - Número de parqueaderos necesarios
        - Aspectos negociables (cosas que podrían ceder)
        - Aspectos no negociables (requisitos indispensables)
        
        Recuerda: una sola pregunta a la vez, de forma natural y conversacional.
        """}
    ]

# Inicializar el estado de la próxima pregunta
if "next_question" not in st.session_state:
    st.session_state.next_question = "tipo_negocio"

# Inicializar mensajes si no existen
if "messages" not in st.session_state:
    st.session_state.messages = []

# Enviar mensaje inicial de NORA si aún no hay mensajes
if not st.session_state.messages:
    initial_message = (
        "Hola, soy NORA, tu asistente inmobiliaria. Estoy aquí para ayudarte a encontrar la propiedad perfecta para ti. "
        "¿Me podrías contar un poco sobre lo que estás buscando? ¿Te interesa comprar o rentar?"
    )
    st.chat_message("assistant").markdown(initial_message)
    st.session_state.messages.append({"role": "assistant", "content": initial_message})
    st.session_state.langchain_messages.append({"role": "assistant", "content": initial_message})

# Mostrar mensajes anteriores en la interfaz
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Mostrar información recopilada y barra de progreso en la barra lateral
with st.sidebar:
    st.subheader("Información recopilada")
    requerimiento = st.session_state.requerimiento_data
    
    # Definir los campos requeridos para el pedido
    required_fields = [
        "tipo_negocio",
        "tiempo_estadia",
        "presupuesto_minimo_compra",
        "presupuesto_maximo_compra",
        "presupuesto_minimo_renta",
        "presupuesto_maximo_renta",
        "habitantes",
        "mascotas",
        "habitaciones",
        "banos",
        "area_minima",
        "area_maxima",
        "parqueaderos",
        "barrio",
        "cercanias",
        "negociables",
        "no_negociables",
        "descripcion",
        "fecha_ideal_entrega",
        "comentarios"
    ]
    
    # Calcular cuántos campos se han completado
    filled = 0
    for field in required_fields:
        value = requerimiento.get(field)
        if field == "tipo_negocio":
            if isinstance(value, dict) and any(value.values()):
                filled += 1
        elif field in ["habitaciones", "banos", "parqueaderos", "habitantes"]:
            if isinstance(value, int) and value > 0:
                filled += 1
        elif field in ["presupuesto_minimo_compra", "presupuesto_maximo_compra", "presupuesto_minimo_renta", "presupuesto_maximo_renta", "area_minima"]:
            if value is not None:
                filled += 1
        else:
            if isinstance(value, str) and value.strip():
                filled += 1
                
    progress = filled / len(required_fields)
    
    st.progress(progress)
    st.write(f"Progreso: {filled} de {len(required_fields)} campos completados")
    
    for key, value in requerimiento.items():
        if value and value != 0 and value != "no" and value != {}:
            if key == "tipo_negocio" and isinstance(value, dict):
                st.write(f"**Tipo de negocio:** {', '.join(k for k, v in value.items() if v)}")
            elif key in ["presupuesto_minimo_compra", "presupuesto_maximo_compra", "presupuesto_minimo_renta", "presupuesto_maximo_renta"] and value:
                st.write(f"**{key.replace('_', ' ').title()}:** ${value:,}")
            else:
                st.write(f"**{key.replace('_', ' ').title()}:** {value}")
    
    if st.button("Reiniciar conversación"):
        st.session_state.messages = []
        st.session_state.langchain_messages = [st.session_state.langchain_messages[0]]
        st.session_state.next_question = "tipo_negocio"
        st.session_state.requerimiento_data = {
            "tipo_negocio": {},
            "tiempo_estadia": None,
            "presupuesto_minimo_compra": None,
            "presupuesto_maximo_compra": None,
            "presupuesto_minimo_renta": None,
            "presupuesto_maximo_renta": None,
            "habitantes": 0,
            "mascotas": "no",
            "area_minima": None,
            "area_maxima": None,
            "habitaciones": 0,
            "banos": 0,
            "parqueaderos": 0,
            "barrio": None,
            "cercanias": None,
            "negociables": None,
            "no_negociables": None,
            "descripcion": "",
            "fecha_ideal_entrega": None,
            "comentarios": None,
            "estado": "pendiente",
            "prioridad": "normal"
        }
        st.rerun()

# Función para extraer información del mensaje del usuario
def extract_information(message, current_data):
    print(f"\n--- PROCESANDO MENSAJE: {message} ---")
    print(f"[DEBUG] Estado actual del requerimiento: {current_data}")
    print(f"[DEBUG] Pregunta actual: {st.session_state.next_question}")
    data = current_data.copy()
    message_lower = message.lower()
    
    # Determinar el tipo de negocio actual
    is_compra = "compra" in str(data.get("tipo_negocio", {}))
    is_arriendo = "arriendo" in str(data.get("tipo_negocio", {}))
    is_inversion = "inversión" in str(data.get("tipo_negocio", {}))
    
    print(f"[DEBUG] Tipo de negocio: Compra={is_compra}, Arriendo={is_arriendo}, Inversión={is_inversion}")
    
    # Determinar el contexto de la pregunta actual
    is_presupuesto_context = st.session_state.next_question in ["presupuesto_compra", "presupuesto_renta"]
    is_ubicacion_context = st.session_state.next_question == "ubicacion"
    is_habitaciones_context = st.session_state.next_question == "habitaciones"
    is_banos_context = st.session_state.next_question == "banos"
    is_area_context = st.session_state.next_question == "area"
    is_parqueaderos_context = st.session_state.next_question == "parqueaderos"
    is_habitantes_context = st.session_state.next_question == "habitantes"
    
    print(f"[DEBUG] Contexto de la pregunta: Presupuesto={is_presupuesto_context}, Ubicación={is_ubicacion_context}, Habitaciones={is_habitaciones_context}, Baños={is_banos_context}, Área={is_area_context}")
    
    # Verificar si el mensaje se refiere a habitantes (prioridad alta)
    is_about_habitantes = re.search(r'(?:somos|vivimos|viviremos|vivirán|viviremos)\s+(\w+|\d+)\s+(?:personas|persona)', message_lower) is not None
    is_about_habitantes = is_about_habitantes or re.search(r'(?:somos|vivimos|viviremos|vivirán|viviremos)\s+(\w+|\d+)', message_lower) is not None
    is_about_habitantes = is_about_habitantes or "hijo" in message_lower or "hijos" in message_lower
    
    if is_about_habitantes:
        print(f"[DEBUG] El mensaje parece referirse a habitantes/personas")
        # Extraer el número de habitantes
        if re.search(r'(?:somos|vivimos|viviremos|vivirán|viviremos)\s+(\w+|\d+)\s+(?:personas|persona)', message_lower):
            match = re.search(r'(?:somos|vivimos|viviremos|vivirán|viviremos)\s+(\w+|\d+)\s+(?:personas|persona)', message_lower)
            num_text = match.group(1)
            if num_text.isdigit():
                data["habitantes"] = int(num_text)
            else:
                num_map = {"una": 1, "un": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6}
                if num_text.lower() in num_map:
                    data["habitantes"] = num_map[num_text.lower()]
            print(f"[OK] Número de habitantes detectados (mención explícita): {data['habitantes']}")
            # Si estamos en la fase de habitaciones, avanzar a la siguiente pregunta
            if st.session_state.next_question == "habitaciones":
                st.session_state.next_question = "banos"
            elif st.session_state.next_question == "habitantes":
                st.session_state.next_question = "mascotas"
        # También capturar patrones como "somos tres"
        elif re.search(r'(?:somos|vivimos|viviremos|vivirán|viviremos)\s+(\w+|\d+)', message_lower):
            match = re.search(r'(?:somos|vivimos|viviremos|vivirán|viviremos)\s+(\w+|\d+)', message_lower)
            num_text = match.group(1)
            if num_text.isdigit():
                data["habitantes"] = int(num_text)
            else:
                num_map = {"una": 1, "un": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6}
                if num_text.lower() in num_map:
                    data["habitantes"] = num_map[num_text.lower()]
            print(f"[OK] Número de habitantes detectados (somos X): {data['habitantes']}")
            # Si estamos en la fase de habitaciones, avanzar a la siguiente pregunta
            if st.session_state.next_question == "habitaciones":
                st.session_state.next_question = "banos"
            elif st.session_state.next_question == "habitantes":
                st.session_state.next_question = "mascotas"
        # Capturar patrones como "yo y mi hijo"
        elif "hijo" in message_lower or "hijos" in message_lower:
            if "un hijo" in message_lower or "mi hijo" in message_lower:
                data["habitantes"] = 2  # Usuario + 1 hijo
            elif "dos hijos" in message_lower or "mis hijos" in message_lower:
                data["habitantes"] = 3  # Usuario + 2 hijos
            else:
                match = re.search(r'(\d+)\s*hijo', message_lower)
                if match:
                    data["habitantes"] = 1 + int(match.group(1))  # Usuario + número de hijos
                else:
                    data["habitantes"] = 2  # Por defecto: usuario + 1 hijo
            print(f"[OK] Número de habitantes detectados (con hijos): {data['habitantes']}")
            if st.session_state.next_question == "habitaciones":
                st.session_state.next_question = "banos"
            elif st.session_state.next_question == "habitantes":
                st.session_state.next_question = "mascotas"
    
    # Extraer tipo de negocio
    if not data["tipo_negocio"] or not any(data["tipo_negocio"].values()):
        if any(word in message_lower for word in ["comprar", "compra", "adquirir", "adquisición"]):
            data["tipo_negocio"] = {"compra": True}
            print("[OK] Tipo de negocio detectado: compra")
            st.session_state.next_question = "presupuesto_compra"
        elif any(word in message_lower for word in ["arrendar", "arriendo", "alquilar", "alquiler", "renta", "rentar"]):
            data["tipo_negocio"] = {"arriendo": True}
            print("[OK] Tipo de negocio detectado: arriendo")
            st.session_state.next_question = "tiempo_estadia"
        elif any(word in message_lower for word in ["invertir", "inversión"]):
            data["tipo_negocio"] = {"inversión": True}
            print("[OK] Tipo de negocio detectado: inversión")
            st.session_state.next_question = "presupuesto_compra"
    
    # Extraer tiempo de estadía (solo para arriendo)
    if "arriendo" in str(data.get("tipo_negocio", {})):
        if data["tiempo_estadia"] is None:
            # Primero, buscar patrones explícitos como "un año", "1 año", etc.
            if any(phrase in message_lower for phrase in ["un año", "un ano", "1 año", "1 ano"]):
                data["tiempo_estadia"] = 12
                print(f"[OK] Tiempo de estadía detectado: 12 meses (1 año)")
                st.session_state.next_question = "presupuesto_renta"
            elif any(phrase in message_lower for phrase in ["dos años", "dos anos", "2 años", "2 anos"]):
                data["tiempo_estadia"] = 24
                print(f"[OK] Tiempo de estadía detectado: 24 meses (2 años)")
                st.session_state.next_question = "presupuesto_renta"
            else:
                # Si no se encuentra un patrón explícito, usar expresiones regulares
                tiempo_patterns = [
                    r'(\d+)\s*(?:mes|meses)',
                    r'(\d+)\s*(?:año|años|ano|anos)',
                    r'(\d+)\s*(?:semana|semanas)'
                ]
                for pattern in tiempo_patterns:
                    match = re.search(pattern, message_lower)
                    if match:
                        periodo = int(match.group(1))
                        if "mes" in pattern:
                            data["tiempo_estadia"] = periodo
                        elif "año" in pattern or "ano" in pattern:
                            data["tiempo_estadia"] = periodo * 12
                        elif "semana" in pattern:
                            data["tiempo_estadia"] = max(1, round(periodo / 4))  # Convertir semanas a meses (mínimo 1)
                        print(f"[OK] Tiempo de estadía detectado: {data['tiempo_estadia']} meses")
                        st.session_state.next_question = "presupuesto_renta"
                        break
    
    # Extraer presupuesto (para compra)
    if "compra" in str(data.get("tipo_negocio", {})) or "inversión" in str(data.get("tipo_negocio", {})):
        if data["presupuesto_minimo_compra"] is None or data["presupuesto_maximo_compra"] is None:
            print(f"[DEBUG] Intentando extraer presupuesto de compra del mensaje: '{message_lower}'")
            
            # Primero verificar si el mensaje es solo un número y estamos en la fase de presupuesto
            if st.session_state.next_question == "presupuesto_compra" and message_lower.strip().isdigit():
                value = int(message_lower.strip())
                data["presupuesto_maximo_compra"] = value
                print(f"[OK] Presupuesto máximo detectado (solo número): {data['presupuesto_maximo_compra']}")
                st.session_state.next_question = "ubicacion"
            # Verificar si hay un rango de presupuesto con la palabra "millones"
            elif "entre" in message_lower and "millones" in message_lower and re.search(r'entre\s+(\d+)\s+y\s+(\d+)\s*millones', message_lower):
                match = re.search(r'entre\s+(\d+)\s+y\s+(\d+)\s*millones', message_lower)
                data["presupuesto_minimo_compra"] = int(match.group(1)) * 1000000
                data["presupuesto_maximo_compra"] = int(match.group(2)) * 1000000
                print(f"[OK] Presupuesto detectado: entre {data['presupuesto_minimo_compra']} y {data['presupuesto_maximo_compra']}")
                if st.session_state.next_question == "presupuesto_compra":
                    st.session_state.next_question = "ubicacion"
            else:
                # Patrones para detectar presupuesto
                patterns = [
                    r'(\d+)\s*millones',
                    r'(\d+[\.\,]?\d*)\s*millones',
                    r'(\d+)[\.\,](\d{3})[\.\,](\d{3})',
                    r'entre\s+(\d+)\s+y\s+(\d+)\s*millones'
                ]
                for pattern in patterns:
                    match = re.search(pattern, message_lower)
                    if match:
                        if pattern == r'entre\s+(\d+)\s+y\s+(\d+)\s*millones':
                            data["presupuesto_minimo_compra"] = int(match.group(1)) * 1000000
                            data["presupuesto_maximo_compra"] = int(match.group(2)) * 1000000
                            print(f"[OK] Presupuesto detectado: entre {data['presupuesto_minimo_compra']} y {data['presupuesto_maximo_compra']}")
                        elif pattern == r'(\d+)[\.\,](\d{3})[\.\,](\d{3})':
                            value = int(match.group(1) + match.group(2) + match.group(3))
                            data["presupuesto_maximo_compra"] = value
                            print(f"[OK] Presupuesto máximo detectado: {data['presupuesto_maximo_compra']}")
                        else:
                            value = float(match.group(1).replace(',', '.')) * 1000000
                            data["presupuesto_maximo_compra"] = int(value)
                            print(f"[OK] Presupuesto máximo detectado: {data['presupuesto_maximo_compra']}")
                        
                        if st.session_state.next_question == "presupuesto_compra":
                            st.session_state.next_question = "ubicacion"
                        break
    
    # Extraer presupuesto (para renta)
    elif "arriendo" in str(data.get("tipo_negocio", {})):
        if data["presupuesto_minimo_renta"] is None or data["presupuesto_maximo_renta"] is None:
            print(f"[DEBUG] Intentando extraer presupuesto de renta del mensaje: '{message_lower}'")
            
            # Primero verificar si el mensaje es solo un número y estamos en la fase de presupuesto
            if st.session_state.next_question == "presupuesto_renta" and message_lower.strip().isdigit():
                value = int(message_lower.strip())
                data["presupuesto_maximo_renta"] = value
                print(f"[OK] Presupuesto máximo renta detectado (solo número): {data['presupuesto_maximo_renta']}")
                st.session_state.next_question = "ubicacion"
            else:
                # Patrones para detectar presupuesto de renta
                patterns = [
                    r'(\d+)\s*millones',
                    r'(\d+[\.\,]?\d*)\s*millones',
                    r'(\d+)[\.\,](\d{3})[\.\,](\d{3})',
                    r'entre\s+(\d+)\s+y\s+(\d+)\s*millones',
                    r'(\d+)[\.\,]?(\d{3})',  # Para valores como 1.500 o 1,500
                    r'(\d+)\s*mil'  # Para valores como "un millón quinientos mil"
                ]
                for pattern in patterns:
                    match = re.search(pattern, message_lower)
                    if match:
                        if pattern == r'entre\s+(\d+)\s+y\s+(\d+)\s*millones':
                            data["presupuesto_minimo_renta"] = int(match.group(1)) * 1000000
                            data["presupuesto_maximo_renta"] = int(match.group(2)) * 1000000
                            print(f"[OK] Presupuesto renta detectado: entre {data['presupuesto_minimo_renta']} y {data['presupuesto_maximo_renta']}")
                        elif pattern == r'(\d+)[\.\,](\d{3})[\.\,](\d{3})':
                            value = int(match.group(1) + match.group(2) + match.group(3))
                            data["presupuesto_maximo_renta"] = value
                            print(f"[OK] Presupuesto máximo renta detectado: {data['presupuesto_maximo_renta']}")
                        elif pattern == r'(\d+)[\.\,]?(\d{3})':
                            value = int(match.group(1)) * 1000 + int(match.group(2))
                            data["presupuesto_maximo_renta"] = value
                            print(f"[OK] Presupuesto máximo renta detectado: {data['presupuesto_maximo_renta']}")
                        elif pattern == r'(\d+)\s*mil':
                            value = int(match.group(1)) * 1000
                            data["presupuesto_maximo_renta"] = value
                            print(f"[OK] Presupuesto máximo renta detectado: {data['presupuesto_maximo_renta']}")
                        else:
                            value = float(match.group(1).replace(',', '.')) * 1000000
                            data["presupuesto_maximo_renta"] = int(value)
                            print(f"[OK] Presupuesto máximo renta detectado: {data['presupuesto_maximo_renta']}")
                        
                        if st.session_state.next_question == "presupuesto_renta":
                            st.session_state.next_question = "ubicacion"
                        break
    
    # Extraer ubicación (barrio/zona)
    if st.session_state.next_question == "ubicacion" or data["barrio"] is None:
        print(f"[DEBUG] Intentando extraer ubicación del mensaje: '{message_lower}'")
        
        # Primero, intentar extraer cualquier texto que parezca una ubicación
        # Esto es más permisivo y capturará cualquier nombre de lugar mencionado
        if any(word in message_lower for word in ["norte", "sur", "este", "oeste", "centro", "zona"]):
            print(f"[DEBUG] Detectada referencia a zona general: {message_lower}")
            data["barrio"] = message_lower.strip().title()
            print(f"[OK] Zona general detectada: {data['barrio']}")
            if st.session_state.next_question == "ubicacion":
                st.session_state.next_question = "habitaciones"
        else:
            # Buscar patrones específicos de ubicación
            locations = re.findall(
                r'(?:en|cerca de|por|zona|barrio|sector|colonia|distrito)\s+([A-Za-zÁáÉéÍíÓóÚúÑñ\s]+?)(?:\.|\,|\s+y|\s+o|\s+para|\s+que|\s+con|\s+es|\s+está|\s+tiene|\s+si|\s+no|\s+$)',
                message_lower
            )
            
            # Si no encontramos con el patrón anterior, intentar extraer cualquier palabra que parezca un nombre propio
            if not locations:
                print("[DEBUG] No se encontró ubicación con el patrón regular, buscando nombres propios")
                # Buscar palabras que empiecen con mayúscula en el mensaje original (posibles nombres de barrios)
                words = message.split()
                for word in words:
                    if word and word[0].isupper() and len(word) > 3:  # Palabras que empiezan con mayúscula y tienen más de 3 letras
                        print(f"[DEBUG] Posible nombre propio encontrado: {word}")
                        data["barrio"] = word.strip()
                        print(f"[OK] Barrio detectado (por nombre propio): {data['barrio']}")
                        if st.session_state.next_question == "ubicacion":
                            st.session_state.next_question = "habitaciones"
                        break
            
            # Si encontramos ubicaciones con el patrón regular
            if locations:
                data["barrio"] = locations[0].strip().title()
                print(f"[OK] Barrio detectado (por patrón): {data['barrio']}")
                if st.session_state.next_question == "ubicacion":
                    st.session_state.next_question = "habitaciones"
            
            # Si el usuario menciona explícitamente un barrio o zona
            explicit_locations = ["manrique", "robledo", "poblado", "laureles", "envigado", "bello", "itagui", "sabaneta"]
            for loc in explicit_locations:
                if loc in message_lower:
                    data["barrio"] = loc.title()
                    print(f"[OK] Barrio explícito detectado: {data['barrio']}")
                    if st.session_state.next_question == "ubicacion":
                        st.session_state.next_question = "habitaciones"
                    break
        
        # Si después de todos los intentos no hemos detectado un barrio y el usuario dice algo como "no importa"
        if (st.session_state.next_question == "ubicacion" and 
            any(phrase in message_lower for phrase in ["no importa", "no me importa", "cualquier", "no tengo preferencia", "no"])):
            data["barrio"] = "Sin preferencia específica"
            print(f"[OK] Usuario no tiene preferencia específica de ubicación")
            st.session_state.next_question = "habitaciones"
    
    # Extraer habitaciones
    if (st.session_state.next_question == "habitaciones" or data["habitaciones"] == 0) and st.session_state.next_question not in ["presupuesto_compra", "presupuesto_renta"] and not is_about_habitantes:
        print(f"[DEBUG] Intentando extraer número de habitaciones del mensaje: '{message_lower}'")
        
        # Primero, buscar patrones explícitos como "3 habitaciones"
        match = re.search(r'(\d+)\s*(?:habitacion|habitaciones|cuarto|cuartos|alcoba|alcobas)', message_lower)
        if match:
            data["habitaciones"] = int(match.group(1))
            print(f"[OK] Número de habitaciones detectadas (patrón completo): {data['habitaciones']}")
            if st.session_state.next_question == "habitaciones":
                st.session_state.next_question = "banos"
        # Si no hay un patrón explícito, verificar si el mensaje es solo un número
        elif message_lower.strip().isdigit() and st.session_state.next_question == "habitaciones":
            data["habitaciones"] = int(message_lower.strip())
            print(f"[OK] Número de habitaciones detectadas (solo número): {data['habitaciones']}")
            if st.session_state.next_question == "habitaciones":
                st.session_state.next_question = "banos"
        # También buscar números escritos como palabras, pero solo si no se refiere a personas
        elif any(word in message_lower for word in ["una", "dos", "tres", "cuatro", "cinco"]) and "persona" not in message_lower and "somos" not in message_lower:
            num_map = {"una": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5}
            for word, num in num_map.items():
                if word in message_lower:
                    data["habitaciones"] = num
                    print(f"[OK] Número de habitaciones detectadas (palabra): {data['habitaciones']}")
                    if st.session_state.next_question == "habitaciones":
                        st.session_state.next_question = "banos"
                    break
    
    # Extraer baños
    if (st.session_state.next_question == "banos" or data["banos"] == 0) and st.session_state.next_question not in ["presupuesto_compra", "presupuesto_renta"] and not is_about_habitantes:
        print(f"[DEBUG] Intentando extraer número de baños del mensaje: '{message_lower}'")
        
        # Primero, buscar patrones explícitos como "2 baños"
        match = re.search(r'(\d+)\s*(?:baño|baños)', message_lower)
        if match:
            data["banos"] = int(match.group(1))
            print(f"[OK] Número de baños detectados (patrón completo): {data['banos']}")
            if st.session_state.next_question == "banos":
                st.session_state.next_question = "area"
        # Mejorar la detección de palabras numéricas para baños
        elif any(word in message_lower for word in ["un", "uno", "dos", "tres", "cuatro"]):
            # Buscar específicamente patrones como "dos baños"
            for word, num in {"un": 1, "uno": 1, "dos": 2, "tres": 3, "cuatro": 4}.items():
                pattern = f"{word}\\s*(?:baño|baños)"
                if re.search(pattern, message_lower):
                    data["banos"] = num
                    print(f"[OK] Número de baños detectados (palabra específica): {data['banos']}")
                    if st.session_state.next_question == "banos":
                        st.session_state.next_question = "area"
                    break
        # Si no hay un patrón explícito, verificar si el mensaje es solo un número
        elif message_lower.strip().isdigit() and st.session_state.next_question == "banos":
            data["banos"] = int(message_lower.strip())
            print(f"[OK] Número de baños detectados (solo número): {data['banos']}")
            if st.session_state.next_question == "banos":
                st.session_state.next_question = "area"
    
    # Extraer área
    if st.session_state.next_question == "area" or data["area_minima"] is None:
        print(f"[DEBUG] Intentando extraer área del mensaje: '{message_lower}'")
        
        # Mejorar la detección de área con patrones más específicos
        area_patterns = [
            r'(\d+)\s*(?:m2|metros|metro|metros cuadrados)',
            r'(\d+)\s*(?:m|mt|mts)(?:\s+cuadrados|\s+2|2|\^2)?'
        ]
        
        for pattern in area_patterns:
            match = re.search(pattern, message_lower)
            if match:
                data["area_minima"] = int(match.group(1))
                print(f"[OK] Área mínima detectada (patrón completo): {data['area_minima']} m2")
                if st.session_state.next_question == "area":
                    st.session_state.next_question = "parqueaderos"
                break
        
        # Si no hay un patrón explícito, verificar si el mensaje contiene un rango de números
        if data["area_minima"] is None and re.search(r'(\d+)\s*(?:a|y|o|-)\s*(\d+)', message_lower) and "millones" not in message_lower and "presupuesto" not in message_lower:
            match = re.search(r'(\d+)\s*(?:a|y|o|-)\s*(\d+)', message_lower)
            data["area_minima"] = int(match.group(1))
            data["area_maxima"] = int(match.group(2))
            print(f"[OK] Área detectada (rango): {data['area_minima']} a {data['area_maxima']} m2")
            if st.session_state.next_question == "area":
                st.session_state.next_question = "parqueaderos"
        # Si no hay un patrón explícito, verificar si el mensaje es solo un número
        elif data["area_minima"] is None and message_lower.strip().isdigit() and st.session_state.next_question == "area":
            data["area_minima"] = int(message_lower.strip())
            print(f"[OK] Área mínima detectada (solo número): {data['area_minima']} m2")
            if st.session_state.next_question == "area":
                st.session_state.next_question = "parqueaderos"
    
    # Extraer parqueaderos
    if (st.session_state.next_question == "parqueaderos" or data["parqueaderos"] == 0) and st.session_state.next_question not in ["presupuesto_compra", "presupuesto_renta"] and not is_about_habitantes:
        print(f"[DEBUG] Intentando extraer número de parqueaderos del mensaje: '{message_lower}'")
        
        match = re.search(r'(\d+)\s*(?:parqueadero|parqueaderos|garaje|garajes)', message_lower)
        if match:
            data["parqueaderos"] = int(match.group(1))
            print(f"[OK] Número de parqueaderos detectados (patrón completo): {data['parqueaderos']}")
            if st.session_state.next_question == "parqueaderos":
                st.session_state.next_question = "habitantes"
        # Si no hay un patrón explícito, verificar si el mensaje es solo un número
        elif message_lower.strip().isdigit() and st.session_state.next_question == "parqueaderos":
            data["parqueaderos"] = int(message_lower.strip())
            print(f"[OK] Número de parqueaderos detectados (solo número): {data['parqueaderos']}")
            if st.session_state.next_question == "parqueaderos":
                st.session_state.next_question = "habitantes"
        # También buscar números escritos como palabras, pero solo si no se refiere a personas
        elif any(word in message_lower for word in ["un", "uno", "dos", "tres", "cuatro"]) and "persona" not in message_lower and "somos" not in message_lower:
            num_map = {"un": 1, "uno": 1, "dos": 2, "tres": 3, "cuatro": 4}
            for word, num in num_map.items():
                if word in message_lower:
                    data["parqueaderos"] = num
                    print(f"[OK] Número de parqueaderos detectados (palabra): {data['parqueaderos']}")
                    if st.session_state.next_question == "parqueaderos":
                        st.session_state.next_question = "habitantes"
                    break
    
    # Extraer mascotas
    if st.session_state.next_question == "mascotas" or data["mascotas"] == "no":
        if any(word in message_lower for word in ["mascota", "mascotas", "perro", "gato", "animal"]):
            data["mascotas"] = "si"
            print("[OK] Se detectó que el usuario tiene mascotas.")
            if st.session_state.next_question == "mascotas":
                st.session_state.next_question = "negociables"
    
    # Extraer aspectos negociables
    if st.session_state.next_question == "negociables" and data["negociables"] is None:
        if "negociable" in message_lower or "podría ceder" in message_lower or "no me importa" in message_lower:
            # Buscar frases después de "negociable", "podría ceder", etc.
            negociables_patterns = [
                r'(?:negociable|podría ceder|no me importa|puedo prescindir)[^\.\,]*([^\.\,]+)',
                r'(?:no necesito|no es indispensable)[^\.\,]*([^\.\,]+)'
            ]
            for pattern in negociables_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    data["negociables"] = match.group(1).strip()
                    print(f"[OK] Aspectos negociables detectados: {data['negociables']}")
                    if st.session_state.next_question == "negociables":
                        st.session_state.next_question = "no_negociables"
                    break
    
    # Extraer aspectos no negociables
    if st.session_state.next_question == "no_negociables" and data["no_negociables"] is None:
        if "no negociable" in message_lower or "indispensable" in message_lower or "necesito que tenga" in message_lower:
            # Buscar frases después de "no negociable", "indispensable", etc.
            no_negociables_patterns = [
                r'(?:no negociable|indispensable|necesito que tenga)[^\.\,]*([^\.\,]+)',
                r'(?:es importante|debe tener|tiene que tener)[^\.\,]*([^\.\,]+)'
            ]
            for pattern in no_negociables_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    data["no_negociables"] = match.group(1).strip()
                    print(f"[OK] Aspectos no negociables detectados: {data['no_negociables']}")
                    if st.session_state.next_question == "no_negociables":
                        st.session_state.next_question = "fecha_entrega"
                    break
    
    # Extraer fecha ideal de entrega
    if st.session_state.next_question == "fecha_entrega" and data["fecha_ideal_entrega"] is None:
        fecha_patterns = [
            r'(?:para|en)\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)',
            r'(?:para|en)\s+(\d+)\s+(?:de)\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)',
            r'(?:para|en)\s+(\d+)\s+(?:mes|meses)',
            r'(?:para|en)\s+(\d+)\s+(?:semana|semanas)'
        ]
        for pattern in fecha_patterns:
            match = re.search(pattern, message_lower)
            if match:
                data["fecha_ideal_entrega"] = match.group(0)
                print(f"[OK] Fecha ideal de entrega detectada: {data['fecha_ideal_entrega']}")
                if st.session_state.next_question == "fecha_entrega":
                    st.session_state.next_question = "comentarios"
                break
    
    # Actualizar descripción
    if data["descripcion"]:
        data["descripcion"] += " " + message
    else:
        data["descripcion"] = message
    
    print(f"[DEBUG] Estado final del requerimiento: {data}")
    print(f"[DEBUG] Próxima pregunta a realizar: {st.session_state.next_question}")
    print("--- FIN DEL PROCESAMIENTO ---\n")
    
    # Mecanismo final: si hemos preguntado por lo mismo más de 3 veces, avanzamos
    if "pregunta_count" not in st.session_state:
        st.session_state.pregunta_count = {}

    if st.session_state.next_question not in st.session_state.pregunta_count:
        st.session_state.pregunta_count[st.session_state.next_question] = 1
    else:
        st.session_state.pregunta_count[st.session_state.next_question] += 1

    # Usar esta lista personalizada en el mecanismo de avance automático
    if st.session_state.pregunta_count.get(st.session_state.next_question, 0) > 3:
        print(f"[AVISO] Se ha preguntado por {st.session_state.next_question} más de 3 veces. Avanzando...")
        
        # Dependiendo de la pregunta en la que estamos atascados, establecemos un valor por defecto
        if st.session_state.next_question == "tiempo_estadia":
            data["tiempo_estadia"] = 12  # Valor por defecto: 1 año
            st.session_state.next_question = "presupuesto_renta"
        elif st.session_state.next_question == "ubicacion":
            data["barrio"] = "Sin preferencia específica"
            st.session_state.next_question = "habitaciones"
        elif st.session_state.next_question == "habitaciones" and data["habitaciones"] == 0:
            data["habitaciones"] = 2  # Valor por defecto: 2 habitaciones
            st.session_state.next_question = "banos"
        elif st.session_state.next_question == "banos" and data["banos"] == 0:
            data["banos"] = 1  # Valor por defecto: 1 baño
            st.session_state.next_question = "area"
        elif st.session_state.next_question == "area" and data["area_minima"] is None:
            data["area_minima"] = 60  # Valor por defecto: 60 m²
            st.session_state.next_question = "parqueaderos"
        elif st.session_state.next_question == "parqueaderos" and data["parqueaderos"] == 0:
            data["parqueaderos"] = 1  # Valor por defecto: 1 parqueadero
            st.session_state.next_question = "habitantes"
        elif st.session_state.next_question == "habitantes" and data["habitantes"] == 0:
            data["habitantes"] = 2  # Valor por defecto: 2 habitantes
            st.session_state.next_question = "mascotas"
        elif st.session_state.next_question == "mascotas":
            data["mascotas"] = "no"  # Valor por defecto: sin mascotas
            st.session_state.next_question = "negociables"
        elif st.session_state.next_question == "negociables":
            data["negociables"] = "Sin preferencias específicas"
            st.session_state.next_question = "no_negociables"
        elif st.session_state.next_question == "no_negociables":
            data["no_negociables"] = "Sin requisitos indispensables específicos"
            st.session_state.next_question = "fecha_entrega"
        elif st.session_state.next_question == "fecha_entrega":
            data["fecha_ideal_entrega"] = "Lo antes posible"
            st.session_state.next_question = "comentarios"
        else:
            # Para cualquier otra pregunta, avanzamos a la siguiente fase
            print(f"[DEBUG] Avanzando a la siguiente fase desde {st.session_state.next_question}")
            next_questions = []
            if "compra" in str(data.get("tipo_negocio", {})) or "inversión" in str(data.get("tipo_negocio", {})):
                next_questions = ["tipo_negocio", "presupuesto_compra", "ubicacion", "habitaciones", "banos", 
                                 "area", "parqueaderos", "habitantes", "mascotas", "negociables", 
                                 "no_negociables", "fecha_entrega", "comentarios"]
            elif "arriendo" in str(data.get("tipo_negocio", {})):
                next_questions = ["tipo_negocio", "tiempo_estadia", "presupuesto_renta", "ubicacion", 
                                 "habitaciones", "banos", "area", "parqueaderos", "habitantes", 
                                 "mascotas", "negociables", "no_negociables", "fecha_entrega", "comentarios"]
            else:
                next_questions = ["tipo_negocio", "tiempo_estadia", "presupuesto_compra", "presupuesto_renta", 
                                 "ubicacion", "habitaciones", "banos", "area", "parqueaderos", 
                                 "habitantes", "mascotas", "negociables", "no_negociables", 
                                 "fecha_entrega", "comentarios"]
            current_index = next_questions.index(st.session_state.next_question) if st.session_state.next_question in next_questions else -1
            if current_index >= 0 and current_index < len(next_questions) - 1:
                st.session_state.next_question = next_questions[current_index + 1]
                print(f"[DEBUG] Nueva pregunta: {st.session_state.next_question}")
        
        # Reiniciar el contador
        st.session_state.pregunta_count[st.session_state.next_question] = 0
    
    return data

# Procesar el input del usuario
if prompt := st.chat_input("Escribe tu pregunta..."):
    # Mostrar el mensaje del usuario
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Extraer información del mensaje del usuario y actualizar en tiempo real
    with st.spinner("NORA está procesando tu mensaje..."):
        # Extraer información y actualizar el estado
        st.session_state.requerimiento_data = extract_information(prompt, st.session_state.requerimiento_data)
        
        # Añadir el mensaje del usuario al historial de LangChain
        st.session_state.langchain_messages.append({"role": "user", "content": prompt})
        
        # Incluir la información recopilada y la próxima pregunta en el contexto
        requerimiento_info = json.dumps(st.session_state.requerimiento_data, ensure_ascii=False)
        next_question_info = st.session_state.next_question
        
        context_message = {
            "role": "system",
            "content": f"""
            Información recopilada hasta ahora: {requerimiento_info}
            
            La próxima información que debes obtener es: {next_question_info}
            
            INSTRUCCIONES IMPORTANTES:
            1. El usuario está interesado en: {', '.join(k for k, v in st.session_state.requerimiento_data["tipo_negocio"].items() if v)}
            2. NO preguntes sobre otros tipos de negocio (como arriendo si el usuario quiere comprar, o viceversa).
            3. Haz SOLO UNA PREGUNTA relacionada con {next_question_info}.
            4. Mantén un tono conversacional y natural.
            5. No menciones explícitamente que estás siguiendo un guion o recopilando datos específicos.
            6. No preguntes por información que ya tienes.
            7. Adapta tu pregunta al contexto de la conversación.
            """
        }
        
        # Convertir mensajes al formato requerido por LangChain
        langchain_format_messages = []
        for msg in st.session_state.langchain_messages:
            if msg["role"] == "system":
                langchain_format_messages.append(["system", msg["content"]])
            elif msg["role"] == "user":
                langchain_format_messages.append(["human", msg["content"]])
            elif msg["role"] == "assistant":
                langchain_format_messages.append(["ai", msg["content"]])
        
        # Añadir el mensaje de contexto
        langchain_format_messages.append(["system", context_message["content"]])
        
        # Obtener la respuesta del modelo
        response = llm.invoke(langchain_format_messages).content
        
        # Mostrar la respuesta en la interfaz
        with st.chat_message("assistant"):
            st.markdown(response)
        
        # Guardar la respuesta en los historiales
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.langchain_messages.append({"role": "assistant", "content": response})
        
        # Forzar la actualización de la barra lateral
        st.rerun()
