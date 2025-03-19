import json
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from langchain_openai import ChatOpenAI

# Cargar variables de entorno
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def agent_tool(resumen=None, respuestas=None, agente_id=12, propietario_id=None):
    """
    Esta función:
      1. Recibe el resumen y las respuestas sobre la propiedad.
      2. Estructura la información en un JSON acorde al modelo PropiedadModel de Django.
      3. Envía la información a la API para crear la propiedad.
      
    Args:
        resumen (str, optional): Resumen generado previamente.
        respuestas (dict, optional): Respuestas del usuario para cada aspecto.
        agente_id (int, optional): ID del agente. Por defecto es 12.
        propietario_id (int, optional): ID del propietario. Puede ser None.
    """
    # Validar entradas
    if respuestas is None:
        respuestas = {}
    
    print("Procesando resumen de propiedad:\n", resumen)
    print(f"Agente ID: {agente_id}, Propietario ID: {propietario_id}")

    # Generar un payload con valores predeterminados
    payload = {
        "agente": agente_id,
        "propietario": propietario_id,
        "titulo": respuestas.get("titulo", ""),
        "tipo_propiedad": respuestas.get("tipo_propiedad", ""),
        "descripcion": respuestas.get("descripcion", resumen),  # Usar el resumen como descripción si no hay otra
        "modalidad_de_negocio": None,
        "direccion": None,
        "nivel": None,
        "metro_cuadrado_construido": None,
        "metro_cuadrado_propiedad": None,
        "habitaciones": None,
        "habitacion_de_servicio": None,
        "banos": None,
        "terraza": "no",
        "balcon": "no",
        "garajes": None,
        "depositos": None,
        "mascotas": "no"
    }
    
    try:
        # Intentar transformar respuestas en formato adecuado
        if "modalidad_de_negocio" in respuestas and respuestas["modalidad_de_negocio"]:
            try:
                # Intentar interpretar como JSON
                if isinstance(respuestas["modalidad_de_negocio"], str):
                    payload["modalidad_de_negocio"] = json.loads(respuestas["modalidad_de_negocio"])
                else:
                    payload["modalidad_de_negocio"] = respuestas["modalidad_de_negocio"]
            except json.JSONDecodeError:
                # Si no es JSON, crear un objeto simple
                modalidad = respuestas["modalidad_de_negocio"].lower()
                if "venta" in modalidad:
                    payload["modalidad_de_negocio"] = {"operacion": "venta"}
                elif "alquiler" in modalidad or "arriendo" in modalidad:
                    payload["modalidad_de_negocio"] = {"operacion": "alquiler"}
                else:
                    payload["modalidad_de_negocio"] = {"operacion": modalidad}
        
        # Procesar direccion
        if "direccion" in respuestas and respuestas["direccion"]:
            try:
                if isinstance(respuestas["direccion"], str):
                    # Convertir dirección texto a objeto
                    payload["direccion"] = {
                        "direccion": respuestas["direccion"],
                        "datos_adicionales": {}
                    }
                else:
                    payload["direccion"] = respuestas["direccion"]
            except Exception:
                payload["direccion"] = {"direccion": respuestas["direccion"]}
        
        # Procesar campos numéricos
        campos_numericos = [
            "nivel", "metro_cuadrado_construido", "metro_cuadrado_propiedad",
            "habitaciones", "habitacion_de_servicio", "banos"
        ]
        
        for campo in campos_numericos:
            if campo in respuestas and respuestas[campo]:
                try:
                    valor = respuestas[campo]
                    if isinstance(valor, str):
                        # Extraer números de texto como "2 habitaciones"
                        import re
                        numeros = re.findall(r'\d+', valor)
                        if numeros:
                            payload[campo] = int(numeros[0])
                    else:
                        payload[campo] = int(valor)
                except ValueError:
                    print(f"No se pudo convertir '{campo}' a número: {respuestas[campo]}")
        
        # Procesar campos booleanos o de selección
        if "terraza" in respuestas and respuestas["terraza"]:
            if any(palabra in respuestas["terraza"].lower() for palabra in ["sí", "si", "tiene", "cuenta con"]):
                payload["terraza"] = "si"
        
        if "balcon" in respuestas and respuestas["balcon"]:
            if any(palabra in respuestas["balcon"].lower() for palabra in ["sí", "si", "tiene", "cuenta con"]):
                payload["balcon"] = "si"
        
        if "mascotas" in respuestas and respuestas["mascotas"]:
            if any(palabra in respuestas["mascotas"].lower() for palabra in ["sí", "si", "permite", "admite"]):
                payload["mascotas"] = "si"
        
        # Procesar campos JSON
        if "garajes" in respuestas and respuestas["garajes"]:
            try:
                if isinstance(respuestas["garajes"], str):
                    # Extraer número de garajes
                    import re
                    numeros = re.findall(r'\d+', respuestas["garajes"])
                    if numeros:
                        payload["garajes"] = {"cantidad": numeros[0]}
                else:
                    payload["garajes"] = respuestas["garajes"]
            except Exception:
                payload["garajes"] = {"cantidad": "1"}
        
        if "depositos" in respuestas and respuestas["depositos"]:
            try:
                if isinstance(respuestas["depositos"], str):
                    # Extraer número de depósitos
                    import re
                    numeros = re.findall(r'\d+', respuestas["depositos"])
                    if numeros:
                        payload["depositos"] = {"cantidad": numeros[0]}
                else:
                    payload["depositos"] = respuestas["depositos"]
            except Exception:
                payload["depositos"] = {"cantidad": "1"}
        
        # Generar título si no existe
        if not payload["titulo"] or payload["titulo"] == "":
            # Crear un título basado en la información disponible
            tipo = payload["tipo_propiedad"] if payload["tipo_propiedad"] else "Propiedad"
            habitaciones = f" de {payload['habitaciones']} habitaciones" if payload["habitaciones"] else ""
            ubicacion = f" en {payload['direccion']['direccion']}" if payload["direccion"] and "direccion" in payload["direccion"] else ""
            
            payload["titulo"] = f"{tipo.capitalize()}{habitaciones}{ubicacion}"
        
        # Usar LLM para estructurar mejor los datos y completar faltantes
        prompt_structure = (
            f"Analiza esta información de una propiedad inmobiliaria y estructura correctamente los campos según el formato requerido:\n\n"
            f"Resumen: {resumen}\n\n"
            f"Payload actual: {json.dumps(payload, indent=2, ensure_ascii=False)}\n\n"
            f"Mejora y completa los datos según las siguientes reglas:\n"
            f"1. modalidad_de_negocio debe ser un objeto JSON con 'operacion' ('venta'/'alquiler'/'ambos') y opcionalmente 'precio'\n"
            f"2. direccion debe ser un objeto JSON con 'direccion' (texto) y opcionalmente 'datos_adicionales'\n"
            f"3. garajes y depositos deben ser objetos JSON con al menos una propiedad 'cantidad'\n"
            f"4. mascotas, terraza y balcon deben ser 'si' o 'no'\n"
            f"5. Asegúrate de inferir datos faltantes del resumen si es posible\n\n"
            f"Devuelve solo el objeto JSON mejorado sin ningún texto adicional."
        )
        
        llm = ChatOpenAI(model_name="gpt-4", temperature=0.2, openai_api_key=OPENAI_API_KEY)
        llm_output = llm.predict(prompt_structure)
        print("Respuesta LLM:", llm_output[:150] + "..." if len(llm_output) > 150 else llm_output)
        
        # Encontrar el JSON en la respuesta
        json_start = llm_output.find('{')
        json_end = llm_output.rfind('}')
        
        if json_start >= 0 and json_end > json_start:
            json_str = llm_output[json_start:json_end+1]
            extracted_data = json.loads(json_str)
            
            # Actualizar el payload con los datos estructurados
            for key, value in extracted_data.items():
                if key in payload and value is not None:
                    payload[key] = value
                    
            print("Datos estructurados correctamente")
        else:
            print("No se pudo encontrar JSON válido en la respuesta, usando datos originales")
    
    except Exception as e:
        print(f"Error al procesar datos de la propiedad: {str(e)}")
        # Continuamos con el payload básico

    # Realizar el llamado a la API para crear la propiedad
    api_url = "http://localhost:8000/crm/propiedadAI/"

    try:
        print("Enviando payload a la API:", json.dumps(payload)[:100] + "..." if len(json.dumps(payload)) > 100 else json.dumps(payload))
        response = requests.post(api_url, json=payload)
        if response.status_code == 201:
            print("Propiedad creada exitosamente:")
            print(response.json())
            return True, response.json()
        else:
            print("Error al crear la propiedad:")
            print(response.status_code, response.text)
            return False, {"error": f"Error {response.status_code}: {response.text}"}
    except Exception as e:
        print("Excepción al realizar la solicitud POST:", str(e))
        return False, {"error": str(e)}

# Ejecutar el agent tool solo cuando se llama directamente
if __name__ == "__main__":
    # Ejemplo de uso directo
    print("Ejecutando propiedadTool directamente...")
    
    # Ejemplo de resumen para pruebas
    ejemplo_resumen = """
    Se trata de un apartamento de 3 habitaciones y 2 baños ubicado en el norte de la ciudad.
    Cuenta con un área de 120 metros cuadrados, balcón y terraza. Tiene 1 parqueadero y 1 depósito.
    Está en un quinto piso, permite mascotas y se ofrece en venta por 350 millones de pesos.
    """
    
    # Ejemplo de respuestas
    ejemplo_respuestas = {
        "tipo_propiedad": "apartamento",
        "modalidad_de_negocio": "venta",
        "habitaciones": "3",
        "banos": "2",
        "direccion": "Calle 123 #45-67, Norte de la ciudad",
        "nivel": "5",
        "metro_cuadrado_construido": "120",
        "terraza": "si",
        "balcon": "si",
        "garajes": "1",
        "depositos": "1",
        "mascotas": "si"
    }
    
    exito, resultado = agent_tool(ejemplo_resumen, ejemplo_respuestas)
    
    if exito:
        print("Propiedad creada exitosamente con ID:", resultado.get("id", "No disponible"))
    else:
        print("Error:", resultado.get("error", "Desconocido")) 