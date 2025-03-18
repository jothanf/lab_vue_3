from django.urls import path
from . import views

urlpatterns = [
    path('chat_room/<str:room_name>/', views.chat_room, name='chat_room'),
    path('chat_context/', views.chat_context, name='chat_context'),
    path('chat_room_context/<str:room_name>/<str:context_type>/<int:item_id>/', views.chat_room_context, name='chat_room_context'),
    path('api/get_context_data/<str:context_type>/<int:item_id>/', views.get_context_data, name='get_context_data'),
    path('api/chat_with_agent/', views.chat_with_agent, name='chat_with_agent'),
    path('api/requerimiento_inmobiliario_agente/', views.requerimiento_inmobiliario_agente, name='requerimiento_inmobiliario_agente'),
]