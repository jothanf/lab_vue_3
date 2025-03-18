import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .IA_services.IA_services import AIService
from crm.models import EdificioModel
from .data_services.data_fetchers import DataFetcher

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.ai_service = AIService()
        
        # Extraer el tipo de contexto y el ID del room_name
        context_info = self.room_name.split('_')
        if len(context_info) >= 2:
            self.context_type = context_info[0]
            self.item_id = context_info[1]
            
            # Obtener el contexto según el tipo
            fetcher = DataFetcher()
            if self.context_type == 'edificio':
                self.context_data = await fetcher.get_edificio_data(self.item_id)
            elif self.context_type == 'propiedad':
                self.context_data = await fetcher.get_propiedad_data(self.item_id)
            elif self.context_type == 'localidad':
                self.context_data = await fetcher.get_localidad_data(self.item_id)
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')
        
        # Enviar mensaje del usuario al chat
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'is_user': True
            }
        )
        
        # Procesar con OpenAI usando el contexto
        respuesta = await sync_to_async(self.ai_service.chat_with_gpt)(
            message, 
            self.context_type, 
            self.context_data
        )
        
        # Enviar respuesta de OpenAI
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': respuesta,
                'is_user': False
            }
        )

    async def chat_message(self, event):
        message = event['message']
        is_user = event['is_user']

        await self.send(text_data=json.dumps({
            'message': message,
            'is_user': is_user
        })) 