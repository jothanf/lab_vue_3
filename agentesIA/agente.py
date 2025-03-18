import os
from typing import Dict, List, Tuple, Any
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from .tools.inventarioTool import obtener_todas_propiedades, buscar_propiedades, InventarioTool
from .tools.agendaTool import AgendaTool, obtener_agentes_disponibles
from agentesIA.tools.requerimientoTool import get_requerimiento_tool

# Cargar variables de entorno
load_dotenv()

# Definir el modelo de lenguaje
llm = ChatOpenAI(model="gpt-3.5-turbo")

# Mensaje de sistema para definir el comportamiento del agente
SYSTEM_MESSAGE = """
Eres NORA (Navegador de Operaciones Real Estate Automatizado), una asistente inmobiliaria profesional especializada en el mercado Colombiano.

Tu objetivo es ayudar a los clientes a encontrar propiedades que se ajusten a sus necesidades, responder preguntas sobre bienes raíces y proporcionar información valiosa sobre el proceso de compra/venta de inmuebles.

Conocimientos que posees:
- Información detallada sobre propiedades en venta
- Tendencias del mercado inmobiliario colombiano
- Procesos de compra, venta y financiamiento
- Aspectos legales básicos de transacciones inmobiliarias
- Consejos para inversión en bienes raíces

Cuando interactúes con clientes:
1. Sé profesional, amable y empática
2. Utiliza terminología inmobiliaria apropiada
3. Proporciona información precisa sobre las propiedades
4. Haz preguntas para entender mejor las necesidades del cliente
5. Ofrece alternativas cuando sea apropiado
6. Responde en español, utilizando términos inmobiliarios correctos

IMPORTANTE: 
- Siempre que te pregunten por propiedades disponibles, debes consultar la base de datos real utilizando la herramienta de inventario.
- Cuando un cliente quiera agendar una cita, utiliza la herramienta de agenda para crear la cita directamente.
"""

def procesar_mensaje(mensaje: str, historial: List[Any] = None, cliente_id: str = None) -> Tuple[str, List[Any]]:
    """
    Procesa un mensaje del usuario y devuelve la respuesta del agente.
    
    Args:
        mensaje: El mensaje del usuario
        historial: Lista opcional de mensajes previos
        cliente_id: ID del cliente que está interactuando con el agente
        
    Returns:
        Tupla con (respuesta, nuevo_historial)
    """
    print("\n===== INICIO DE PROCESAMIENTO DE MENSAJE =====")
    print(f"Mensaje recibido: '{mensaje}'")
    print(f"Cliente ID: {cliente_id}")
    
    # Inicializar historial si es None
    if historial is None:
        print("Historial vacío, iniciando nueva conversación")
        historial = []
    else:
        print(f"Historial existente con {len(historial)} mensajes")
    
    # Crear mensaje del usuario
    user_message = HumanMessage(content=mensaje)
    
    # Preparar mensajes incluyendo historial y mensaje del sistema
    if not historial:
        print("Añadiendo mensaje del sistema al inicio de la conversación")
        system_message = SystemMessage(content=SYSTEM_MESSAGE)
        mensajes = [system_message, user_message]
    else:
        mensajes = historial + [user_message]
    
    # Detectar si el mensaje está relacionado con propiedades
    palabras_clave_propiedades = [
        "propiedad", "propiedades", "casa", "apartamento", "lote", "terreno", 
        "oficina", "local", "inmueble", "inmuebles", "venta", "arriendo", 
        "alquiler", "comprar", "rentar", "disponible", "disponibles", 
        "inventario", "mostrar", "ver", "listar", "económica", "economica",
        "barata", "precio"
    ]
    
    # Detectar si el mensaje está relacionado con agendar una cita
    palabras_clave_agenda = [
        "agendar", "cita", "reunión", "reunion", "visita", "programar", 
        "calendario", "agenda", "disponibilidad", "horario", "fecha", 
        "hora", "día", "dia", "semana", "mes", "contactar", "hablar", 
        "conocer", "entrevistar", "consultar"
    ]
    
    # Palabras clave que indican una solicitud explícita de crear una cita
    palabras_clave_crear_cita = [
        "crear", "agendar", "programar", "reservar", "quiero una cita", 
        "necesito una cita", "hacer una cita", "concertar", "confirmar"
    ]
    
    # Palabras clave que indican una consulta de disponibilidad
    palabras_clave_disponibilidad = [
        "disponibilidad", "disponible", "horarios", "cuando", "qué días", 
        "que dias", "qué horas", "que horas", "tienes tiempo", "hay espacio"
    ]
    
    palabras_encontradas_propiedades = [palabra for palabra in palabras_clave_propiedades if palabra in mensaje.lower()]
    es_consulta_propiedades = len(palabras_encontradas_propiedades) > 0
    
    palabras_encontradas_agenda = [palabra for palabra in palabras_clave_agenda if palabra in mensaje.lower()]
    es_consulta_agenda = len(palabras_encontradas_agenda) > 0
    
    palabras_encontradas_crear_cita = [palabra for palabra in palabras_clave_crear_cita if palabra in mensaje.lower()]
    es_solicitud_crear_cita = len(palabras_encontradas_crear_cita) > 0
    
    palabras_encontradas_disponibilidad = [palabra for palabra in palabras_clave_disponibilidad if palabra in mensaje.lower()]
    es_consulta_disponibilidad = len(palabras_encontradas_disponibilidad) > 0
    
    print(f"¿Es consulta de propiedades? {es_consulta_propiedades}")
    print(f"¿Es consulta de agenda? {es_consulta_agenda}")
    print(f"¿Es solicitud explícita de crear cita? {es_solicitud_crear_cita}")
    print(f"¿Es consulta de disponibilidad? {es_consulta_disponibilidad}")
    
    # Si es una consulta de disponibilidad, responder con opciones
    if es_consulta_agenda and es_consulta_disponibilidad and not es_solicitud_crear_cita:
        try:
            print("Procesando consulta de disponibilidad...")
            
            # Obtener lista de agentes disponibles
            agentes = obtener_agentes_disponibles()
            if not agentes:
                print("No se pudieron obtener los agentes disponibles")
                respuesta_disponibilidad = "Lo siento, no pude obtener la lista de agentes disponibles en este momento. Por favor, intente más tarde o contacte directamente con la oficina."
                ai_message = AIMessage(content=respuesta_disponibilidad)
                mensajes.append(ai_message)
                return respuesta_disponibilidad, mensajes
            
            print(f"Se encontraron {len(agentes)} agentes disponibles")
            
            # Extraer información de fecha si se menciona
            import re
            import datetime
            
            fecha_mencionada = None
            hoy = datetime.datetime.now()
            
            # Detectar "fin de semana"
            if "fin de semana" in mensaje.lower() or "finde" in mensaje.lower():
                # Calcular el próximo sábado
                dias_hasta_sabado = (5 - hoy.weekday()) % 7
                if dias_hasta_sabado == 0:
                    dias_hasta_sabado = 7  # Si hoy es sábado, ir al próximo
                
                proximo_sabado = hoy + datetime.timedelta(days=dias_hasta_sabado)
                proximo_domingo = proximo_sabado + datetime.timedelta(days=1)
                
                fecha_mencionada = f"el fin de semana ({proximo_sabado.strftime('%d/%m/%Y')} y {proximo_domingo.strftime('%d/%m/%Y')})"
            
            # Detectar "próxima semana"
            elif "próxima semana" in mensaje.lower() or "proxima semana" in mensaje.lower():
                # Calcular el lunes de la próxima semana
                dias_hasta_lunes = (0 - hoy.weekday()) % 7
                if dias_hasta_lunes == 0:
                    dias_hasta_lunes = 7  # Si hoy es lunes, ir al próximo
                
                proximo_lunes = hoy + datetime.timedelta(days=dias_hasta_lunes)
                proximo_viernes = proximo_lunes + datetime.timedelta(days=4)
                
                fecha_mencionada = f"la próxima semana (del {proximo_lunes.strftime('%d/%m/%Y')} al {proximo_viernes.strftime('%d/%m/%Y')})"
            
            # Detectar días específicos
            dias_semana = {
                'lunes': 0, 'martes': 1, 'miércoles': 2, 'miercoles': 2, 
                'jueves': 3, 'viernes': 4, 'sábado': 5, 'sabado': 5, 'domingo': 6
            }
            
            for dia, num in dias_semana.items():
                if f"próximo {dia}" in mensaje.lower() or f"proximo {dia}" in mensaje.lower():
                    dias_hasta = (num - hoy.weekday()) % 7
                    if dias_hasta == 0:
                        dias_hasta = 7  # Si hoy es el mismo día, ir al próximo
                    
                    proximo_dia = hoy + datetime.timedelta(days=dias_hasta)
                    fecha_mencionada = f"el próximo {dia} ({proximo_dia.strftime('%d/%m/%Y')})"
                    break
            
            # Si no se detectó ninguna fecha específica
            if not fecha_mencionada:
                fecha_mencionada = "en los próximos días"
            
            # Crear respuesta con opciones de disponibilidad
            respuesta_disponibilidad = f"¡Claro! Tenemos disponibilidad para agendar citas {fecha_mencionada}. Estos son nuestros agentes disponibles:\n\n"
            
            for i, agente in enumerate(agentes, 1):
                nombre = f"{agente.get('user', {}).get('first_name', '')} {agente.get('user', {}).get('last_name', '')}"
                respuesta_disponibilidad += f"{i}. {nombre}\n"
            
            respuesta_disponibilidad += "\nLos horarios disponibles son:\n"
            respuesta_disponibilidad += "- Mañana: 9:00 AM a 12:00 PM\n"
            respuesta_disponibilidad += "- Tarde: 2:00 PM a 6:00 PM\n\n"
            
            respuesta_disponibilidad += "¿Te gustaría agendar una cita con alguno de nuestros agentes? Por favor, indícame con quién, qué día y a qué hora te gustaría reunirte."
            
            # Añadir la respuesta al historial
            print("Añadiendo respuesta de disponibilidad al historial")
            ai_message = AIMessage(content=respuesta_disponibilidad)
            mensajes.append(ai_message)
            
            print("===== FIN DE PROCESAMIENTO DE MENSAJE =====\n")
            return respuesta_disponibilidad, mensajes
            
        except Exception as e:
            print(f"ERROR al procesar consulta de disponibilidad: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Si es una solicitud explícita de crear una cita, proceder con la creación
    elif es_consulta_agenda and es_solicitud_crear_cita:
        try:
            print("Procesando solicitud de creación de cita...")
            
            # Obtener lista de agentes disponibles primero
            agentes = obtener_agentes_disponibles()
            if not agentes:
                print("No se pudieron obtener los agentes disponibles")
                respuesta_agenda = "Lo siento, no pude obtener la lista de agentes disponibles en este momento. Por favor, intente más tarde o contacte directamente con la oficina."
                ai_message = AIMessage(content=respuesta_agenda)
                mensajes.append(ai_message)
                return respuesta_agenda, mensajes
            
            print(f"Se encontraron {len(agentes)} agentes disponibles")
            # Imprimir los IDs de los agentes para depuración
            for agente in agentes:
                print(f"Agente disponible: ID={agente.get('id')}, Nombre={agente.get('user', {}).get('first_name', '')} {agente.get('user', {}).get('last_name', '')}")
            
            # Crear una instancia de la herramienta de agenda
            agenda_tool = AgendaTool()
            
            # Asignar el cliente_id a la herramienta
            if cliente_id:
                agenda_tool.cliente_id = cliente_id
                print(f"Cliente ID asignado a la herramienta: {cliente_id}")
            else:
                print("ADVERTENCIA: No se proporcionó cliente_id")
                respuesta_agenda = "Lo siento, no puedo crear una agenda sin identificar al cliente. Por favor inicie sesión."
                ai_message = AIMessage(content=respuesta_agenda)
                mensajes.append(ai_message)
                return respuesta_agenda, mensajes
            
            # Extraer información de la agenda del mensaje
            import re
            import datetime
            
            # Extraer ID o nombre del agente
            agente_id = None
            agente_match = re.search(r'agente (\d+)', mensaje.lower())
            if agente_match:
                agente_id_texto = agente_match.group(1)
                print(f"ID de agente detectado en texto: {agente_id_texto}")
                
                # Verificar que el ID existe en la lista de agentes
                agente_id_valido = None
                for agente in agentes:
                    if str(agente.get('id')) == agente_id_texto:
                        agente_id_valido = agente.get('id')
                        print(f"ID de agente validado: {agente_id_valido}")
                        break
                
                if agente_id_valido:
                    agente_id = agente_id_valido
                else:
                    print(f"ADVERTENCIA: El ID de agente {agente_id_texto} no existe en la base de datos")
            
            # Si no se encontró por ID, buscar por nombre
            if not agente_id:
                print("Buscando agente por nombre...")
                for agente in agentes:
                    nombre_completo = f"{agente.get('user', {}).get('first_name', '')} {agente.get('user', {}).get('last_name', '')}".lower()
                    first_name = agente.get('user', {}).get('first_name', '').lower() if agente.get('user', {}).get('first_name') else ""
                    
                    print(f"Comparando con: {first_name} / {nombre_completo}")
                    
                    if first_name and first_name in mensaje.lower():
                        agente_id = agente.get('id')
                        print(f"Agente encontrado por nombre: {first_name} (ID: {agente_id})")
                        break
                    elif nombre_completo and nombre_completo in mensaje.lower():
                        agente_id = agente.get('id')
                        print(f"Agente encontrado por nombre completo: {nombre_completo} (ID: {agente_id})")
                        break
                    # Buscar coincidencias parciales
                    elif first_name and len(first_name) > 2:
                        palabras = mensaje.lower().split()
                        for palabra in palabras:
                            if first_name in palabra or palabra in first_name:
                                agente_id = agente.get('id')
                                print(f"Agente encontrado por coincidencia parcial: {first_name} / {palabra} (ID: {agente_id})")
                            break
        
            # Si aún no hay agente_id, usar el primer agente disponible
            if not agente_id and agentes:
                agente_id = agentes[0].get('id')
                print(f"Usando primer agente disponible por defecto: {agente_id}")
            
            # Extraer fecha
            fecha = None
            fecha_match = re.search(r'(\d{4}-\d{2}-\d{2})', mensaje)
            if fecha_match:
                fecha = fecha_match.group(1)
                print(f"Fecha detectada en formato ISO: {fecha}")
            else:
                # Intentar detectar fechas en formato más natural
                hoy = datetime.datetime.now()
                print(f"Fecha actual: {hoy.strftime('%Y-%m-%d')}")
                
                # Detectar "mañana"
                if "mañana" in mensaje.lower() or "manana" in mensaje.lower():
                    manana = hoy + datetime.timedelta(days=1)
                    fecha = manana.strftime('%Y-%m-%d')
                    print(f"Fecha calculada para mañana: {fecha}")
                
                # Detectar "fin de semana"
                elif "fin de semana" in mensaje.lower() or "finde" in mensaje.lower():
                    # Calcular el próximo sábado
                    dias_hasta_sabado = (5 - hoy.weekday()) % 7
                    if dias_hasta_sabado == 0:
                        dias_hasta_sabado = 7  # Si hoy es sábado, ir al próximo
                    
                    proximo_sabado = hoy + datetime.timedelta(days=dias_hasta_sabado)
                    fecha = proximo_sabado.strftime('%Y-%m-%d')
                    print(f"Fecha calculada para el próximo sábado: {fecha}")
                
                # Detectar fechas en formato "14 de marzo de 2025"
                fecha_natural_match = re.search(r'(\d{1,2}) de (enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre) de (\d{4})', mensaje.lower())
                if fecha_natural_match:
                    dia = int(fecha_natural_match.group(1))
                    mes = fecha_natural_match.group(2)
                    ano = int(fecha_natural_match.group(3))
                    
                    meses = {
                        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
                        'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
                    }
                    
                    mes_num = meses.get(mes, 1)
                    
                    try:
                        fecha_dt = datetime.datetime(ano, mes_num, dia)
                        fecha = fecha_dt.strftime('%Y-%m-%d')
                        print(f"Fecha detectada en formato natural: {fecha}")
                    except ValueError:
                        print(f"Fecha inválida: {dia}/{mes_num}/{ano}")
                
                # Detectar "próximo sábado", "próximo lunes", etc.
                dias_semana = {
                    'lunes': 0, 'martes': 1, 'miércoles': 2, 'miercoles': 2, 
                    'jueves': 3, 'viernes': 4, 'sábado': 5, 'sabado': 5, 'domingo': 6
                }
                
                for dia, num in dias_semana.items():
                    if f"próximo {dia}" in mensaje.lower() or f"proximo {dia}" in mensaje.lower():
                        # Calcular la fecha del próximo día de la semana mencionado
                        dias_hasta = (num - hoy.weekday()) % 7
                        if dias_hasta == 0:
                            dias_hasta = 7  # Si hoy es el mismo día, ir al próximo
                        
                        proximo_dia = hoy + datetime.timedelta(days=dias_hasta)
                        fecha = proximo_dia.strftime('%Y-%m-%d')
                        print(f"Fecha calculada para próximo {dia}: {fecha}")
                        break
                
                # Si no se detectó ninguna fecha, usar una fecha por defecto (mañana)
                if not fecha:
                    manana = hoy + datetime.timedelta(days=1)
                    fecha = manana.strftime('%Y-%m-%d')
                    print(f"Usando fecha por defecto (mañana): {fecha}")
            
            # Extraer hora
            hora = None
            hora_match = re.search(r'(\d{1,2}):(\d{2})', mensaje)
            if hora_match:
                hora_h = int(hora_match.group(1))
                hora_m = hora_match.group(2)
                hora = f"{hora_h:02d}:{hora_m}:00"
                print(f"Hora detectada con formato HH:MM: {hora}")
            else:
                # Buscar horas sin minutos (por ejemplo, "a las 3")
                hora_simple_match = re.search(r'a las (\d{1,2})', mensaje.lower())
                if hora_simple_match:
                    hora_h = int(hora_simple_match.group(1))
                    hora = f"{hora_h:02d}:00:00"
                    print(f"Hora simple detectada: {hora}")
                else:
                    # Buscar referencias a "medio día" o "mediodía"
                    if "medio dia" in mensaje.lower() or "mediodía" in mensaje.lower() or "medio día" in mensaje.lower():
                        hora = "12:00:00"
                        print(f"Hora detectada (medio día): {hora}")
                    # Buscar referencias a "tarde"
                    elif "tarde" in mensaje.lower():
                        hora = "15:00:00"
                        print(f"Hora detectada (tarde): {hora}")
                    # Buscar referencias a "mañana" (como momento del día)
                    elif "mañana" in mensaje.lower() and "por la mañana" in mensaje.lower():
                        hora = "10:00:00"
                        print(f"Hora detectada (mañana): {hora}")
                    else:
                        # Si no se detectó ninguna hora, usar una hora por defecto (10:00)
                        hora = "10:00:00"
                        print(f"Usando hora por defecto: {hora}")
            
            # Extraer notas
            notas = None
            notas_match = re.search(r'para (ver|hablar|consultar|discutir) (.*?)(\.|$)', mensaje.lower())
            if notas_match:
                notas = notas_match.group(2).strip()
                print(f"Notas detectadas: {notas}")
            else:
                # Si no hay notas específicas, usar todo el mensaje como nota
                notas = f"Solicitud original: {mensaje}"
                print(f"Usando mensaje completo como notas")
            
            # Si tenemos la información necesaria, crear la agenda
            if agente_id and fecha and hora:
                print("Información completa para crear agenda, procediendo...")
                print(f"Datos finales: agente_id={agente_id}, fecha={fecha}, hora={hora}, notas={notas}")
                
                resultado = agenda_tool._run(
                    agente_id=agente_id,
                    fecha=fecha,
                    hora=hora,
                    notas=notas
                )
                
                if resultado.get("success"):
                    # Obtener el nombre del agente para la respuesta
                    nombre_agente = "el agente seleccionado"
                    for agente in agentes:
                        if agente.get('id') == agente_id:
                            nombre_agente = f"{agente.get('user', {}).get('first_name', '')} {agente.get('user', {}).get('last_name', '')}"
                            break
                    
                    respuesta_agenda = f"""
¡Excelente! He agendado tu cita con éxito:

- Fecha: {fecha}
- Hora: {hora}
- Agente: {nombre_agente} (ID: {agente_id})
- Notas: {notas or 'No se proporcionaron notas'}

Tu cita ha sido registrada en nuestro sistema. El agente se pondrá en contacto contigo para confirmar los detalles. Si necesitas modificar o cancelar la cita, por favor házmelo saber.
"""
                else:
                    respuesta_agenda = f"""
Lo siento, no pude agendar la cita debido a un error: {resultado.get('error')}

Por favor, verifica la información e intenta nuevamente, o contacta directamente con nuestra oficina para programar tu cita.
"""
                
                # Añadir la respuesta de agenda a los mensajes
                print("Añadiendo respuesta al historial de mensajes")
                ai_message = AIMessage(content=respuesta_agenda)
                mensajes.append(ai_message)
                
                print("===== FIN DE PROCESAMIENTO DE MENSAJE =====\n")
                return respuesta_agenda, mensajes
            else:
                print(f"Información incompleta para crear agenda: agente_id={agente_id}, fecha={fecha}, hora={hora}")
                
                # Crear una respuesta solicitando la información faltante
                respuesta_agenda = "Para agendar tu cita, necesito la siguiente información:\n\n"
                
                if not agente_id:
                    respuesta_agenda += "- El agente con el que deseas reunirte. Estos son los agentes disponibles:\n"
                    for i, agente in enumerate(agentes, 1):
                        nombre = f"{agente.get('user', {}).get('first_name', '')} {agente.get('user', {}).get('last_name', '')}"
                        respuesta_agenda += f"  {i}. {nombre} (ID: {agente.get('id')})\n"
                
                if not fecha:
                    respuesta_agenda += "- La fecha para la cita (puedes decir 'mañana', 'próximo lunes' o una fecha específica como '15 de marzo de 2025')\n"
                
                if not hora:
                    respuesta_agenda += "- La hora para la cita (por ejemplo, '14:30' o 'a las 3 de la tarde')\n"
                
                respuesta_agenda += "\nPor favor, proporciona la información faltante para que pueda agendar tu cita."
                
                # Añadir la respuesta de agenda a los mensajes
                print("Añadiendo respuesta solicitando información faltante")
                ai_message = AIMessage(content=respuesta_agenda)
                mensajes.append(ai_message)
                
                print("===== FIN DE PROCESAMIENTO DE MENSAJE =====\n")
                return respuesta_agenda, mensajes
            
        except Exception as e:
            print(f"ERROR al procesar solicitud de agenda: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Generar una respuesta de error
            respuesta_error = f"""
Lo siento, ocurrió un error al procesar tu solicitud de agenda: {str(e)}

Por favor, intenta nuevamente con un formato más claro, por ejemplo:
"Quiero agendar una cita con el agente 12 para mañana a las 14:30 para ver propiedades en el centro"
"""
            ai_message = AIMessage(content=respuesta_error)
            mensajes.append(ai_message)
            
            print("===== FIN DE PROCESAMIENTO DE MENSAJE =====\n")
            return respuesta_error, mensajes
    
    # Si es una consulta general de agenda, mostrar opciones
    elif es_consulta_agenda:
        try:
            print("Procesando consulta general de agenda...")
            
            # Obtener agentes disponibles
            agentes = obtener_agentes_disponibles()
            if not agentes:
                print("No se pudieron obtener los agentes disponibles")
                respuesta_agenda = "Lo siento, no pude obtener la lista de agentes disponibles en este momento. Por favor, intente más tarde o contacte directamente con la oficina."
            else:
                print(f"Se encontraron {len(agentes)} agentes disponibles")
                
                # Crear una respuesta con los agentes disponibles
                respuesta_agenda = "Puedo ayudarte a agendar una cita con uno de nuestros agentes. Estos son los agentes disponibles:\n\n"
                
                for i, agente in enumerate(agentes, 1):
                    nombre = f"{agente.get('user', {}).get('first_name', '')} {agente.get('user', {}).get('last_name', '')}"
                    respuesta_agenda += f"{i}. {nombre} (ID: {agente.get('id')})\n"
                
                respuesta_agenda += "\nLos horarios disponibles son:\n"
                respuesta_agenda += "- Mañana: 9:00 AM a 12:00 PM\n"
                respuesta_agenda += "- Tarde: 2:00 PM a 6:00 PM\n\n"
                
                respuesta_agenda += "Para agendar una cita, necesito la siguiente información:\n"
                respuesta_agenda += "- El agente con el que deseas reunirte\n"
                respuesta_agenda += "- La fecha deseada (formato: YYYY-MM-DD o puedes decir 'mañana' o 'próximo lunes')\n"
                respuesta_agenda += "- La hora deseada (formato: HH:MM o puedes decir 'a las 3')\n"
                respuesta_agenda += "- Cualquier nota o detalle adicional sobre la reunión\n\n"
                respuesta_agenda += "Por ejemplo, puedes decirme: 'Quiero agendar una cita con Ana para mañana a las 14:30 para ver propiedades en el centro'."
            
            # Añadir la respuesta de agenda a los mensajes
            print("Añadiendo respuesta al historial de mensajes")
            ai_message = AIMessage(content=respuesta_agenda)
            mensajes.append(ai_message)
            
            print("===== FIN DE PROCESAMIENTO DE MENSAJE =====\n")
            return respuesta_agenda, mensajes
            
        except Exception as e:
            print(f"ERROR al procesar solicitud de agenda: {str(e)}")
            import traceback
            traceback.print_exc()
            # Si hay un error, continuar con la respuesta general
    
    # Si es una consulta de propiedades, buscar en la base de datos
    elif es_consulta_propiedades:
        try:
            print("Analizando consulta para extraer criterios de búsqueda...")
            # Extraer posibles criterios de búsqueda
            criterios = {}
            
            # Tipos de propiedad
            tipos_propiedad = ["casa", "apartamento", "lote", "terreno", "oficina", "local"]
            for tipo in tipos_propiedad:
                if tipo in mensaje.lower():
                    criterios["tipo"] = tipo
                    print(f"Tipo de propiedad detectado: {tipo}")
                    break
            
            # Ubicaciones comunes
            ubicaciones = ["bogota", "medellin", "cali", "barranquilla", "cartagena"]
            for ubicacion in ubicaciones:
                if ubicacion in mensaje.lower():
                    criterios["ubicacion"] = ubicacion
                    print(f"Ubicación detectada: {ubicacion}")
                    break
            
            # Características
            if "terraza" in mensaje.lower():
                criterios["caracteristicas"] = ["Terraza"]
                print("Característica detectada: Terraza")
            elif "balcon" in mensaje.lower() or "balcón" in mensaje.lower():
                criterios["caracteristicas"] = ["Balcón"]
                print("Característica detectada: Balcón")
            
            # Precio
            if "económica" in mensaje.lower() or "economica" in mensaje.lower() or "barata" in mensaje.lower():
                criterios["precio_max"] = 300000
                print("Filtro de precio máximo aplicado: 300,000")
            elif "lujo" in mensaje.lower() or "cara" in mensaje.lower():
                criterios["precio_min"] = 400000
                print("Filtro de precio mínimo aplicado: 400,000")
            
            # Modalidad de negocio
            if "venta" in mensaje.lower() or "comprar" in mensaje.lower():
                criterios["tipo_negocio"] = "Venta"
                print("Modalidad de negocio: Venta")
            elif "arriendo" in mensaje.lower() or "alquiler" in mensaje.lower() or "rentar" in mensaje.lower():
                criterios["tipo_negocio"] = "Renta"
                print("Modalidad de negocio: Renta")
            
            # Limitar resultados
            criterios["limit"] = 5
            
            print(f"Criterios finales de búsqueda: {criterios}")
            print("Consultando base de datos...")
            propiedades = buscar_propiedades(criterios)
            print(f"Se encontraron {len(propiedades)} propiedades en la base de datos")
            
            # Si no se encontraron propiedades con los criterios, mostrar algunas disponibles
            if not propiedades:
                print("No se encontraron propiedades con los criterios específicos. Mostrando propiedades disponibles...")
                propiedades = obtener_todas_propiedades()
                if propiedades:
                    print(f"Se obtuvieron {len(propiedades)} propiedades del inventario general")
                    # Limitar a 5 propiedades
                    propiedades_limitadas = {}
                    for i, (key, value) in enumerate(propiedades.items()):
                        if i >= 5:
                            break
                        propiedades_limitadas[key] = value
                    propiedades = propiedades_limitadas
                    print(f"Limitando a {len(propiedades)} propiedades para mostrar")
            
            # Formatear la respuesta con las propiedades encontradas
            if propiedades:
                print("Formateando respuesta con propiedades encontradas...")
                respuesta_propiedades = f"He encontrado {len(propiedades)} propiedades que coinciden con sus criterios:\n\n"
                
                for i, (prop_id, propiedad) in enumerate(propiedades.items(), 1):
                    print(f"Propiedad {i}: ID={prop_id}, Nombre={propiedad.get('nombre', 'Sin nombre')}")
                    print(f"  Tipo: {propiedad.get('tipo', 'No especificado')}")
                    print(f"  Ubicación: {propiedad.get('ubicacion', 'No especificada')}")
                    print(f"  Precio: {propiedad.get('precio', 0)} {propiedad.get('moneda', 'MXN')}")
                    print(f"  Tipo de negocio: {propiedad.get('tipo_negocio', 'No especificado')}")
                    
                    formato_precio = f"{propiedad.get('precio', 0):,} {propiedad.get('moneda', 'MXN')}"
                    tipo_negocio = propiedad.get('tipo_negocio', 'No especificado')
                    respuesta_propiedades += f"""
**{i}. {propiedad.get('nombre', f'Propiedad {i}')} - {propiedad.get('tipo', 'No especificado')}**
UBICACION: {propiedad.get('ubicacion', 'No especificada')}
PRECIO: {formato_precio} ({tipo_negocio})
DETALLES: {propiedad.get('habitaciones', 0)} hab, {propiedad.get('baños', 0)} baños, {propiedad.get('superficie', 0)} m²
"""
                    if propiedad.get('caracteristicas'):
                        respuesta_propiedades += f"CARACTERISTICAS DESTACADAS: {', '.join(propiedad.get('caracteristicas', [])[:3])}\n"
                    
                    respuesta_propiedades += "\n"
                
                respuesta_propiedades += """
¿Le gustaría obtener más información sobre alguna de estas propiedades? Puede indicarme el número o el nombre de la que le interese, o si prefiere, podemos agendar una cita con uno de nuestros agentes para verlas personalmente.
"""
                
                # Añadir la respuesta de propiedades a los mensajes
                print("Añadiendo respuesta al historial de mensajes")
                ai_message = AIMessage(content=respuesta_propiedades)
                mensajes.append(ai_message)
                
                print("===== FIN DE PROCESAMIENTO DE MENSAJE =====\n")
                return respuesta_propiedades, mensajes
            
        except Exception as e:
            print(f"ERROR al buscar propiedades: {str(e)}")
            # Si hay un error, continuar con la respuesta general
    
    # Para cualquier otro tipo de mensaje o si hubo un error en la búsqueda de propiedades
    print("Generando respuesta general con el modelo de lenguaje...")
    response = llm.invoke(mensajes)
    mensajes.append(response)
    
    print("===== FIN DE PROCESAMIENTO DE MENSAJE =====\n")
    return response.content, mensajes
