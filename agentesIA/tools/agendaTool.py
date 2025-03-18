from typing import Type, List, Dict, Optional, Any
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from datetime import datetime, time
import requests
import json
import logging

# Configurar logging
logger = logging.getLogger(__name__)

class AgendaQuerySchema(BaseModel):
    """Esquema para crear una agenda o cita con un agente inmobiliario."""
    agente_id: int = Field(..., description="ID del agente con el que se desea agendar la cita")
    fecha: str = Field(..., description="Fecha de la cita en formato YYYY-MM-DD")
    hora: str = Field(..., description="Hora de la cita en formato HH:MM:00")
    notas: Optional[str] = Field(None, description="Notas o detalles adicionales sobre la cita")

class AgendaTool(BaseTool):
    """Herramienta para crear agendas o citas con agentes inmobiliarios."""
    name: str = "crear_agenda"
    description: str = """
    Crea una agenda o cita con un agente inmobiliario.
    Útil cuando un cliente quiere programar una cita o reunión con un agente.
    """
    args_schema: Type[BaseModel] = AgendaQuerySchema
    return_direct: bool = False
    cliente_id: Optional[str] = None

    def _run(self, agente_id: int, fecha: str, hora: str, notas: Optional[str] = None) -> Dict[str, Any]:
        """
        Crea una agenda o cita con un agente inmobiliario.
        
        Args:
            agente_id: ID del agente con el que se desea agendar la cita
            fecha: Fecha de la cita en formato YYYY-MM-DD
            hora: Hora de la cita en formato HH:MM:00
            notas: Notas o detalles adicionales sobre la cita
            
        Returns:
            Diccionario con la información de la agenda creada o un mensaje de error
        """
        try:
            logger.info(f"Creando agenda para cliente_id={self.cliente_id}, agente_id={agente_id}")
            
            # Validar formato de fecha y hora
            try:
                datetime.strptime(fecha, '%Y-%m-%d')
                datetime.strptime(hora, '%H:%M:%S')
            except ValueError:
                return {
                    "success": False,
                    "error": "Formato de fecha u hora incorrecto. Use YYYY-MM-DD para fecha y HH:MM:SS para hora."
                }
            
            # Verificar que tenemos un cliente_id
            if not self.cliente_id:
                return {
                    "success": False,
                    "error": "No se pudo identificar al cliente. Por favor inicie sesión."
                }
            
            # Crear la agenda usando la API
            url = "http://127.0.0.1:8000/crm/agenda/"  # URL directa en lugar de usar settings
            
            # Datos para la creación de la agenda
            data = {
                "cliente": self.cliente_id,
                "agente": agente_id,
                "fecha": fecha,
                "hora": hora,
                "estado": "pendiente",
                "notas": notas or "Cita agendada por NORA"
            }
            
            logger.info(f"Enviando datos de agenda: {data}")
            
            # Realizar la petición POST
            response = requests.post(url, json=data)
            
            if response.status_code == 201:  # Creado exitosamente
                agenda_data = response.json()
                logger.info(f"Agenda creada exitosamente: {agenda_data}")
                return {
                    "success": True,
                    "message": "Cita agendada exitosamente",
                    "agenda": agenda_data
                }
            else:
                error_msg = "Error desconocido al crear la agenda"
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict):
                        error_msg = str(error_data)
                except:
                    error_msg = f"Error {response.status_code}: {response.text}"
                
                logger.error(f"Error al crear agenda: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except Exception as e:
            logger.exception(f"Excepción al crear agenda: {str(e)}")
            return {
                "success": False,
                "error": f"Error al crear la agenda: {str(e)}"
            }

def obtener_agentes_disponibles() -> List[Dict[str, Any]]:
    """
    Obtiene la lista de agentes disponibles para agendar citas.
    
    Returns:
        Lista de diccionarios con información de los agentes
    """
    try:
        # Usar URL directa en lugar de settings.BASE_URL
        url = "http://127.0.0.1:8000/accounts/agente/"
        logger.info(f"Obteniendo agentes desde: {url}")
        
        response = requests.get(url)
        
        if response.status_code == 200:
            agentes = response.json()
            logger.info(f"Se encontraron {len(agentes)} agentes")
            return agentes
        else:
            logger.error(f"Error al obtener agentes: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        logger.exception(f"Excepción al obtener agentes: {str(e)}")
        return []
