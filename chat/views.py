from django.shortcuts import render, get_object_or_404, redirect
from crm.models import EdificioModel, PropiedadModel, LocalidadModel
from django.http import JsonResponse
from .data_services.data_fetchers import DataFetcher
from .IA_services.context_builders import AIContextBuilder
from rest_framework.decorators import api_view
from rest_framework.response import Response
from agentesIA.agente import procesar_mensaje
from langchain_core.messages import HumanMessage, AIMessage
from agentesIA.tools.requerimientoTool import get_requerimiento_tool

def chat_room(request, room_name):
    # Obtener el edificio (por ahora hardcodeado como id=1)
    edificio = get_object_or_404(EdificioModel, id=1)
    
    # Crear un contexto estructurado con la información del edificio
    edificio_context = {
        'nombre': edificio.nombre,
        'direccion': edificio.direccion,
        'descripcion': edificio.descripcion,
        'estado': edificio.estado,
        'tipo_edificio': edificio.tipo_edificio,
        'estrato': edificio.estrato,
        'unidades': edificio.unidades,
        'torres': edificio.torres,
        'parqueaderos': edificio.parqueaderos,
        'ano_construccion': edificio.ano_construccion,
        'servicios_adicionales': edificio.servicios_adicionales,
    }
    
    return render(request, 'chat_room.html', {
        'room_name': room_name,
        'edificio_context': edificio_context
    })

async def get_context_data(request, context_type, item_id):
    fetcher = DataFetcher()
    
    context_methods = {
        'edificio': fetcher.get_edificio_data,
        'propiedad': fetcher.get_propiedad_data,
        'localidad': fetcher.get_localidad_data,
    }
    
    if context_type not in context_methods:
        return JsonResponse({'error': 'Tipo de contexto no válido'}, status=400)
    
    try:
        data = await context_methods[context_type](item_id)
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def chat_context(request):
    if request.method == 'POST':
        context_type = request.POST.get('context_type')
        item_id = request.POST.get('item_id')
        
        print(f"DEBUG - POST recibido: context_type={context_type}, item_id={item_id}")  # DEBUG

        # Si se seleccionó un elemento específico
        if 'select_item' in request.POST and item_id:
            print(f"DEBUG - Redirigiendo a chat_room_context con: type={context_type}, id={item_id}")  # DEBUG
            return redirect('chat_room_context', room_name=f"{context_type}_{item_id}", context_type=context_type, item_id=item_id)

        # Si solo se seleccionó el tipo de contexto
        if context_type == 'edificio':
            edificios = EdificioModel.objects.all()
            return render(request, 'chat_context.html', {
                'chat_context': context_type, 
                'edificios': edificios
            })
        elif context_type == 'propiedad':
            propiedades = PropiedadModel.objects.all()
            return render(request, 'chat_context.html', {
                'chat_context': context_type, 
                'propiedades': propiedades
            })
        elif context_type == 'localidad':
            localidades = LocalidadModel.objects.all()
            return render(request, 'chat_context.html', {
                'chat_context': context_type, 
                'localidades': localidades
            })

    return render(request, 'chat_context.html')

async def chat_room_context(request, room_name, context_type, item_id):
    print(f"DEBUG - Entrando a chat_room_context: type={context_type}, id={item_id}")  # DEBUG
    
    fetcher = DataFetcher()
    
    try:
        if context_type == 'edificio':
            print("DEBUG - Procesando contexto de edificio")  # DEBUG
            edificio_data = await fetcher.get_edificio_data(item_id)
            context_agent = AIContextBuilder.build_edificio_context(edificio_data)
        elif context_type == 'propiedad':
            print("DEBUG - Procesando contexto de propiedad")  # DEBUG
            propiedad_data = await fetcher.get_propiedad_data(item_id)
            context_agent = AIContextBuilder.build_propiedad_context(propiedad_data)
        elif context_type == 'localidad':
            print("DEBUG - Procesando contexto de localidad")  # DEBUG
            localidad_data = await fetcher.get_localidad_data(item_id)
            context_agent = AIContextBuilder.build_localidad_context(localidad_data)
        else:
            print(f"DEBUG - Tipo de contexto no válido: {context_type}")  # DEBUG
            context_agent = "Tipo de contexto no válido."
    except Exception as e:
        print(f"DEBUG - Error al procesar contexto: {str(e)}")  # DEBUG
        context_agent = f"Error al procesar contexto: {str(e)}"

    return render(request, 'chat_room_context.html', {
        'room_name': room_name,
        'context_type': context_type,
        'item_id': item_id,
        'context_agent': context_agent
    })

# Versión actualizada de la vista para el chat con el agente NORA
@api_view(['POST'])
def chat_with_agent(request):
    """
    Endpoint para procesar mensajes del chat con el agente NORA.
    """
    try:
        data = request.data
        mensaje = data.get('message', '')
        
        # Obtener el cliente_id del request
        cliente_id = data.get('cliente_id')
        print(f"Cliente ID recibido en la solicitud: {cliente_id}")
        
        # Recuperar el historial de conversación de la base de datos
        historial_mensajes = []
        if cliente_id:
            try:
                from chat.models import ConversationHistory
                historial, created = ConversationHistory.objects.get_or_create(user_id=cliente_id)
                historial_mensajes = historial.messages
                print(f"Historial recuperado para cliente {cliente_id}: {len(historial_mensajes)} mensajes")
            except Exception as e:
                print(f"Error al recuperar historial: {str(e)}")
                historial_mensajes = []
        
        # Convertir el historial a objetos de LangChain
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
        historial_langchain = []
        
        if historial_mensajes:
            for msg in historial_mensajes:
                if msg.get('role') == 'user':
                    historial_langchain.append(HumanMessage(content=msg.get('content', '')))
                elif msg.get('role') == 'assistant':
                    historial_langchain.append(AIMessage(content=msg.get('content', '')))
                elif msg.get('role') == 'system':
                    historial_langchain.append(SystemMessage(content=msg.get('content', '')))
        
        # Procesar el mensaje usando el agente
        respuesta, nuevo_historial = procesar_mensaje(mensaje, historial_langchain, cliente_id)
        
        # Guardar el nuevo historial en la base de datos
        if cliente_id:
            try:
                from chat.models import ConversationHistory
                historial, created = ConversationHistory.objects.get_or_create(user_id=cliente_id)
                
                # Convertir el historial de LangChain a formato JSON
                historial_json = []
                for msg in nuevo_historial:
                    if isinstance(msg, HumanMessage):
                        historial_json.append({'role': 'user', 'content': msg.content})
                    elif isinstance(msg, AIMessage):
                        historial_json.append({'role': 'assistant', 'content': msg.content})
                    elif isinstance(msg, SystemMessage):
                        historial_json.append({'role': 'system', 'content': msg.content})
                
                historial.messages = historial_json
                historial.save()
                print(f"Historial guardado para cliente {cliente_id}: {len(historial_json)} mensajes")
            except Exception as e:
                print(f"Error al guardar historial: {str(e)}")
        
        # Limpiar la respuesta de caracteres problemáticos
        respuesta_limpia = ''
        try:
            # Eliminar emojis y caracteres especiales problemáticos
            import re
            
            # Patrón para detectar emojis y otros caracteres Unicode problemáticos
            emoji_pattern = re.compile(
                "["
                "\U0001F600-\U0001F64F"  # emoticones
                "\U0001F300-\U0001F5FF"  # símbolos y pictogramas
                "\U0001F680-\U0001F6FF"  # transporte y símbolos de mapas
                "\U0001F700-\U0001F77F"  # símbolos alquímicos
                "\U0001F780-\U0001F7FF"  # símbolos geométricos
                "\U0001F800-\U0001F8FF"  # símbolos misceláneos
                "\U0001F900-\U0001F9FF"  # símbolos suplementarios
                "\U0001FA00-\U0001FA6F"  # símbolos extendidos
                "\U0001FA70-\U0001FAFF"  # símbolos extendidos-A
                "\U00002702-\U000027B0"  # dingbats
                "\U000024C2-\U0001F251" 
                "]+", flags=re.UNICODE)
            
            if isinstance(respuesta, str):
                # Eliminar emojis
                respuesta = emoji_pattern.sub(r'', respuesta)
                
                # Convertir a ASCII y de vuelta a UTF-8 para eliminar caracteres problemáticos
                respuesta_limpia = respuesta.encode('ascii', 'ignore').decode('ascii')
                
                # Reemplazar caracteres especiales del español
                respuesta_limpia = respuesta_limpia.replace('á', 'a')
                respuesta_limpia = respuesta_limpia.replace('é', 'e')
                respuesta_limpia = respuesta_limpia.replace('í', 'i')
                respuesta_limpia = respuesta_limpia.replace('ó', 'o')
                respuesta_limpia = respuesta_limpia.replace('ú', 'u')
                respuesta_limpia = respuesta_limpia.replace('ñ', 'n')
                respuesta_limpia = respuesta_limpia.replace('Á', 'A')
                respuesta_limpia = respuesta_limpia.replace('É', 'E')
                respuesta_limpia = respuesta_limpia.replace('Í', 'I')
                respuesta_limpia = respuesta_limpia.replace('Ó', 'O')
                respuesta_limpia = respuesta_limpia.replace('Ú', 'U')
                respuesta_limpia = respuesta_limpia.replace('Ñ', 'N')
                respuesta_limpia = respuesta_limpia.replace('▒', '')
            else:
                respuesta_limpia = "Respuesta no valida"
        except Exception as e:
            print(f"Error al limpiar respuesta: {str(e)}")
            respuesta_limpia = "Lo siento, hubo un problema al procesar la respuesta."
        
        return Response({
            'response': respuesta_limpia,
            'history': []  # No enviamos el historial completo para evitar problemas de tamaño
        })
    except Exception as e:
        print(f"Error en chat_with_agent: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'response': f"Lo siento, ha ocurrido un error: {str(e)}",
            'history': []
        }, status=500)

@api_view(['POST'])
def requerimiento_inmobiliario_agente(request):
    """
    Endpoint para procesar mensajes relacionados con requerimientos inmobiliarios.
    Utiliza la herramienta RequerimientoTool para mantener una conversación fluida
    con el usuario y recopilar información sobre sus necesidades inmobiliarias.
    """
    try:
        data = request.data
        mensaje = data.get('message', '')
        cliente_id = data.get('cliente_id')
        historial_conversacion = data.get('historial_conversacion', [])
        datos_recopilados = data.get('datos_recopilados', {})
        
        print(f"Mensaje recibido: {mensaje}")
        print(f"Cliente ID: {cliente_id}")
        print(f"Historial conversación: {len(historial_conversacion)} mensajes")
        
        # Obtener la herramienta de requerimiento
        requerimiento_tool = get_requerimiento_tool()
        
        # Procesar el mensaje con la herramienta
        resultado = requerimiento_tool._run(
            mensaje=mensaje,
            historial_conversacion=historial_conversacion,
            datos_recopilados=datos_recopilados
        )
        
        # Obtener la respuesta y los datos actualizados
        respuesta = resultado.get('respuesta', "Lo siento, no pude procesar tu mensaje correctamente.")
        historial_actualizado = resultado.get('historial_conversacion', historial_conversacion)
        datos_actualizados = resultado.get('datos_recopilados', datos_recopilados)
        
        print(f"Datos recopilados: {datos_actualizados}")
        
        return Response({
            'respuesta': respuesta,
            'historial_conversacion': historial_actualizado,
            'datos_recopilados': datos_actualizados,
            'completado': False  # Por ahora, no marcamos como completado
        })
    
    except Exception as e:
        import traceback
        print(f"Error en requerimiento_inmobiliario_agente: {str(e)}")
        traceback.print_exc()
        return Response({
            'respuesta': f"Lo siento, ha ocurrido un error: {str(e)}",
            'historial_conversacion': historial_conversacion,
            'datos_recopilados': datos_recopilados,
            'completado': False
        }, status=500)

