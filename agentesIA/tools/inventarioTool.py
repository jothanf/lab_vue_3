from typing import Dict, List, Any, Optional, Type, Literal
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from crm.models import PropiedadModel, EdificioModel, LocalidadModel, BarrioModel, ZonaModel

class PropiedadQuerySchema(BaseModel):
    """Esquema para consultar propiedades."""
    id: Optional[int] = Field(None, description="ID específico de la propiedad")
    tipo: Optional[str] = Field(None, description="Tipo de propiedad (casa, apartamento, local, terreno)")
    ubicacion: Optional[str] = Field(None, description="Ubicación o zona de la propiedad")
    precio_min: Optional[int] = Field(None, description="Precio mínimo")
    precio_max: Optional[int] = Field(None, description="Precio máximo")
    habitaciones: Optional[int] = Field(None, description="Número mínimo de habitaciones")
    banos: Optional[int] = Field(None, description="Número mínimo de baños")
    area_min: Optional[int] = Field(None, description="Área mínima en metros cuadrados")
    caracteristicas: Optional[List[str]] = Field(None, description="Lista de características deseadas")
    limit: Optional[int] = Field(10, description="Número máximo de resultados a devolver")

class InventarioTool(BaseTool):
    name: str = "inventario_propiedades"
    description: str = """
    Consulta el inventario de propiedades inmobiliarias disponibles en la base de datos.
    Útil para buscar propiedades según criterios específicos como ubicación, tipo, precio, etc.
    """
    args_schema: Type[BaseModel] = PropiedadQuerySchema
    return_direct: bool = False
    
    def _run(self, id: Optional[int] = None, tipo: Optional[str] = None, 
             ubicacion: Optional[str] = None, precio_min: Optional[int] = None, 
             precio_max: Optional[int] = None, habitaciones: Optional[int] = None,
             banos: Optional[int] = None, area_min: Optional[int] = None,
             caracteristicas: Optional[List[str]] = None, limit: int = 10) -> Dict[str, Any]:
        """
        Ejecuta la consulta de propiedades según los criterios especificados.
        
        Returns:
            Un diccionario con las propiedades encontradas y metadatos de la búsqueda.
        """
        try:
            # Iniciar la consulta base
            query = PropiedadModel.objects.all()
            
            # Aplicar filtros según los parámetros recibidos
            if id is not None:
                query = query.filter(id=id)
                
            if tipo is not None:
                query = query.filter(tipo_propiedad__icontains=tipo)
                
            if ubicacion is not None:
                # Buscar en direcciones (JSON field)
                query = query.filter(direccion__direccion__icontains=ubicacion)
                
                # También buscar en edificios, barrios, zonas y localidades relacionadas
                edificios = EdificioModel.objects.filter(nombre__icontains=ubicacion)
                if edificios.exists():
                    query = query.filter(edificio__in=edificios)
                
            if precio_min is not None or precio_max is not None:
                # Filtrar por precio es más complejo debido a la estructura JSON
                # Esta es una implementación simplificada
                filtered_props = []
                for prop in query:
                    if not prop.modalidad_de_negocio:
                        continue
                        
                    precio = 0
                    if isinstance(prop.modalidad_de_negocio, str):
                        import json
                        try:
                            modalidad = json.loads(prop.modalidad_de_negocio)
                        except:
                            continue
                    else:
                        modalidad = prop.modalidad_de_negocio
                    
                    # Obtener precio de venta o renta
                    if modalidad.get("venta_tradicional", {}).get("activo"):
                        precio = modalidad.get("venta_tradicional", {}).get("precio", 0)
                    elif modalidad.get("renta_tradicional", {}).get("activo"):
                        precio = modalidad.get("renta_tradicional", {}).get("precio", 0)
                    
                    # Aplicar filtros de precio
                    if precio_min is not None and precio < precio_min:
                        continue
                    if precio_max is not None and precio > precio_max:
                        continue
                        
                    filtered_props.append(prop.id)
                
                if filtered_props:
                    query = query.filter(id__in=filtered_props)
                else:
                    query = PropiedadModel.objects.none()
            
            if habitaciones is not None:
                query = query.filter(habitaciones__gte=habitaciones)
                
            if banos is not None:
                query = query.filter(banos__gte=banos)
                
            if area_min is not None:
                query = query.filter(metro_cuadrado_construido__gte=area_min)
            
            # Limitar resultados
            query = query[:limit]
            
            # Formatear resultados
            resultados = {}
            for prop in query:
                # Crear un ID único para la propiedad
                prop_id = f"prop_{prop.id}"
                
                # Extraer modalidad de negocio
                modalidad = {}
                if prop.modalidad_de_negocio:
                    if isinstance(prop.modalidad_de_negocio, str):
                        import json
                        try:
                            modalidad = json.loads(prop.modalidad_de_negocio)
                        except:
                            modalidad = {"tipo": "No especificado"}
                    else:
                        modalidad = prop.modalidad_de_negocio
                
                # Determinar precio basado en modalidad
                precio = 0
                moneda = "MXN"
                tipo_negocio = "No especificado"
                
                if modalidad and "venta_tradicional" in modalidad and modalidad["venta_tradicional"].get("activo"):
                    precio = modalidad["venta_tradicional"].get("precio", 0)
                    tipo_negocio = "Venta"
                elif modalidad and "renta_tradicional" in modalidad and modalidad["renta_tradicional"].get("activo"):
                    precio = modalidad["renta_tradicional"].get("precio", 0)
                    tipo_negocio = "Renta"
                
                # Obtener características
                caracteristicas_prop = []
                if prop.terraza and prop.terraza != "no":
                    caracteristicas_prop.append("Terraza")
                if prop.balcon and prop.balcon != "no":
                    caracteristicas_prop.append("Balcón")
                if prop.estrato:
                    caracteristicas_prop.append(f"Estrato {prop.estrato}")
                if prop.mascotas == "si":
                    caracteristicas_prop.append("Mascotas permitidas")
                
                # Formatear la propiedad
                resultados[prop_id] = {
                    "id": prop.id,
                    "nombre": prop.titulo or f"Propiedad {prop.id}",
                    "tipo": prop.tipo_propiedad or "No especificado",
                    "tipo_negocio": tipo_negocio,
                    "precio": precio,
                    "moneda": moneda,
                    "ubicacion": prop.direccion.get("direccion", "No especificada") if prop.direccion else "No especificada",
                    "superficie": prop.metro_cuadrado_construido or 0,
                    "habitaciones": prop.habitaciones or 0,
                    "baños": prop.banos or 0,
                    "garage": 0,  # No hay campo directo para esto
                    "año_construccion": prop.ano_construccion or 0,
                    "descripcion": prop.descripcion or "Sin descripción",
                    "caracteristicas": caracteristicas_prop,
                    "estado": "Disponible"  # Asumimos que está disponible
                }
                
                # Filtrar por características si se especificaron
                if caracteristicas and resultados[prop_id]:
                    tiene_caracteristicas = True
                    for c in caracteristicas:
                        if not any(c.lower() in caract.lower() for caract in caracteristicas_prop):
                            tiene_caracteristicas = False
                            break
                    
                    if not tiene_caracteristicas:
                        del resultados[prop_id]
            
            return {
                "status": "success",
                "count": len(resultados),
                "propiedades": resultados,
                "filtros_aplicados": {
                    "id": id,
                    "tipo": tipo,
                    "ubicacion": ubicacion,
                    "precio_min": precio_min,
                    "precio_max": precio_max,
                    "habitaciones": habitaciones,
                    "banos": banos,
                    "area_min": area_min,
                    "caracteristicas": caracteristicas,
                    "limit": limit
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error al consultar propiedades: {str(e)}",
                "propiedades": {}
            }
    
    def _arun(self, query: str):
        """Implementación asíncrona (no utilizada)"""
        raise NotImplementedError("InventarioTool no soporta ejecución asíncrona")


# Función auxiliar para obtener todas las propiedades
def obtener_todas_propiedades() -> Dict[str, Dict[str, Any]]:
    """
    Obtiene todas las propiedades de la base de datos y las formatea para el agente.
    
    Returns:
        Un diccionario con información detallada de todas las propiedades.
    """
    tool = InventarioTool()
    resultado = tool._run(limit=100)  # Obtener hasta 100 propiedades
    
    if resultado["status"] == "success":
        return resultado["propiedades"]
    else:
        # Si hay un error, devolver un diccionario vacío
        print(f"ERROR: {resultado['message']}")
        return {}


# Función para buscar propiedades según criterios
def buscar_propiedades(criterios: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Busca propiedades según los criterios especificados.
    
    Args:
        criterios: Diccionario con los criterios de búsqueda.
        
    Returns:
        Un diccionario con las propiedades que coinciden con los criterios.
    """
    tool = InventarioTool()
    resultado = tool._run(**criterios)
    
    if resultado["status"] == "success":
        return resultado["propiedades"]
    else:
        # Si hay un error, devolver un diccionario vacío
        print(f"ERROR: {resultado['message']}")
        return {}
