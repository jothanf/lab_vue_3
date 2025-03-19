import json
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from langchain_openai import ChatOpenAI

# Cargar variables de entorno
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def agent_tool(resumen=None, cliente_id=29, agente_id=12):
    """
    Esta función:
      1. Recibe el resumen del requerimiento.
      2. Estructura la información en un JSON acorde al modelo Django.
      3. Envía la información a la API (requerimientoAI/) para crear el requerimiento.
      
    Args:
        resumen (str, optional): Resumen generado previamente. Si es None, se generará uno nuevo.
        cliente_id (int, optional): ID del cliente. Por defecto es 29.
        agente_id (int, optional): ID del agente. Por defecto es 12.
    """
    # 1. Obtener el resumen
    if resumen is None:
        from requerimiento import generar_resumen
        resumen = generar_resumen()
    
    print("Procesando resumen:\n", resumen)
    print(f"Cliente ID: {cliente_id}, Agente ID: {agente_id}")

    # 2. Generar un payload con valores personalizados
    payload = {
        "agente": agente_id,
        "cliente": cliente_id,
        "descripcion": resumen,
        "tipo_negocio": {"operacion": "", "tipo_propiedad": ""},
        "presupuesto_minimo_compra": None,
        "presupuesto_maximo_compra": None,
        "habitantes": None,
        "area_minima": None,
        "area_maxima": None,
        "habitaciones": None,
        "banos": None,
        "parqueaderos": None,
        "mascotas": None,
        "cercanias": None,
        "fecha_ideal_entrega": None,
        "no_negocibles": None
    }
    
    try:
        # Intentar obtener valores del LLM
        prompt_simple = (
            f"Analiza este resumen inmobiliario y extrae la siguiente información en formato JSON:\n\n"
            f"{resumen}\n\n"
            f"Solo incluye los campos que puedas determinar con certeza, para el resto usa null.\n"
            f"- tipo_negocio (objeto con 'operacion': 'compra'/'alquiler' y 'tipo_propiedad': 'casa'/'apartamento'/etc)\n"
            f"- presupuesto_minimo_compra (número)\n"
            f"- presupuesto_maximo_compra (número)\n" 
            f"- habitantes (número entero)\n"
            f"- area_minima (número entero en m²)\n"
            f"- area_maxima (número entero en m²)\n"
            f"- habitaciones (número entero)\n"
            f"- banos (número entero)\n"
            f"- parqueaderos (número entero)\n"
            f"- mascotas ('si' o 'no')\n"
            f"- cercanias (array de strings)\n"
            f"- fecha_ideal_entrega (fecha ISO 8601)\n"
            f"- no_negocibles (texto)\n"
        )
        
        llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.2, openai_api_key=OPENAI_API_KEY)
        llm_output = llm.predict(prompt_simple)
        print("Respuesta LLM:", llm_output[:150] + "..." if len(llm_output) > 150 else llm_output)
        
        # Encontrar el JSON en la respuesta
        json_start = llm_output.find('{')
        json_end = llm_output.rfind('}')
        
        if json_start >= 0 and json_end > json_start:
            json_str = llm_output[json_start:json_end+1]
            extracted_data = json.loads(json_str)
            
            # Actualizar el payload con los datos extraídos
            for key, value in extracted_data.items():
                if key in payload and value is not None:
                    payload[key] = value
                    
            print("Datos extraídos correctamente")
        else:
            print("No se pudo encontrar JSON válido en la respuesta")
    
    except Exception as e:
        print(f"Error al extraer datos del resumen: {str(e)}")
        # Continuamos con el payload predeterminado

    # 3. Realizar el llamado a la API para crear el requerimiento
    api_url = "http://localhost:8000/crm/requerimientoAI/"  # Ajusta la URL según tu entorno

    try:
        print("Enviando payload a la API:", json.dumps(payload)[:100] + "..." if len(json.dumps(payload)) > 100 else json.dumps(payload))
        response = requests.post(api_url, json=payload)
        if response.status_code == 201:
            print("Requerimiento creado exitosamente:")
            print(response.json())
            return True, response.json()
        else:
            print("Error al crear el requerimiento:")
            print(response.status_code, response.text)
            return False, {"error": f"Error {response.status_code}: {response.text}"}
    except Exception as e:
        print("Excepción al realizar la solicitud POST:", str(e))
        return False, {"error": str(e)}

# Ejecutar el agent tool solo cuando se llama directamente
if __name__ == "__main__":
    # Ejemplo de uso directo
    print("Ejecutando requerimientoTool directamente...")
    
    # Ejemplo de resumen para pruebas
    ejemplo_resumen = """
    El cliente busca comprar un apartamento en la zona norte de la ciudad, 
    con un presupuesto entre 200 y 250 millones de pesos. 
    Necesita 3 habitaciones, 2 baños y al menos 1 parqueadero. 
    Prefiere estar cerca a centros comerciales y parques. 
    Vive con su esposa y dos hijos pequeños. No tienen mascotas.
    """
    
    exito, resultado = agent_tool(ejemplo_resumen)
    
    if exito:
        print("Requerimiento creado exitosamente con ID:", resultado.get("id", "No disponible"))
    else:
        print("Error:", resultado.get("error", "Desconocido"))
