import json
import random
import os
import uuid
from typing import Dict, List, Any
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

# Cargar variables de entorno
load_dotenv()

# Definir el modelo de lenguaje
llm = ChatOpenAI(model="gpt-4o-mini")

# Mensaje de sistema para definir el comportamiento del agente generador de historias
SYSTEM_MESSAGE = """
Eres un experto en el sector inmobiliario y tu tarea es generar historias de usuario realistas y detalladas para una simulación de un sistema de gestión de propiedades.

Cada historia debe ser coherente, detallada y reflejar situaciones reales del mercado inmobiliario. Debes incorporar los puntos clave proporcionados
y crear una narrativa que sea útil para entender las necesidades, motivaciones y comportamientos de los usuarios en el sector inmobiliario. Cada historia debe tener cerca de 1000 palabras.

Las historias deben incluir:
1. Perfil del usuario (edad, ocupación, situación familiar, nombre, etc.)
2. Necesidades y motivaciones inmobiliarias
3. Criterios de búsqueda y preferencias
4. Obstáculos o preocupaciones
5. Comportamiento de búsqueda y toma de decisiones
6. Expectativas sobre el servicio inmobiliario

Utiliza un lenguaje natural, incluye detalles específicos y crea una narrativa coherente que integre todos los puntos clave proporcionados.
"""

def cargar_llaves_primarias(ruta_resumen: str) -> List[str]:
    """
    Carga las llaves primarias desde el archivo resumen.json
    
    Args:
        ruta_resumen: Ruta al archivo resumen.json
        
    Returns:
        Lista de llaves primarias
    """
    try:
        with open(ruta_resumen, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("Puntos_clave_historia_de_usuario", [])
    except Exception as e:
        print(f"Error al cargar las llaves primarias: {e}")
        return []

def cargar_diccionario_valores(ruta_dic: str) -> Dict[str, List[Any]]:
    """
    Carga el diccionario con todos los valores posibles para cada llave
    
    Args:
        ruta_dic: Ruta al archivo dic.json
        
    Returns:
        Diccionario con las llaves y sus posibles valores
    """
    try:
        with open(ruta_dic, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error al cargar el diccionario de valores: {e}")
        return {}

def generar_combinaciones_aleatorias(
    llaves_primarias: List[str], 
    diccionario_valores: Dict[str, List[Any]], 
    cantidad: int
) -> List[Dict[str, Any]]:
    """
    Genera combinaciones aleatorias de valores para cada llave primaria
    
    Args:
        llaves_primarias: Lista de llaves primarias
        diccionario_valores: Diccionario con los valores posibles para cada llave
        cantidad: Número de combinaciones a generar
        
    Returns:
        Lista de diccionarios con las combinaciones aleatorias
    """
    combinaciones = []
    
    for i in range(cantidad):
        combinacion = {}
        for llave in llaves_primarias:
            # Verificar si la llave existe en el diccionario
            if llave in diccionario_valores and diccionario_valores[llave]:
                # Seleccionar un valor aleatorio de los posibles
                combinacion[llave] = random.choice(diccionario_valores[llave])
            else:
                # Si la llave no existe o no tiene valores, asignar None
                combinacion[llave] = None
                print(f"Advertencia: La llave '{llave}' no existe en el diccionario o no tiene valores")
        
        combinaciones.append(combinacion)
    
    return combinaciones

def guardar_combinaciones(combinaciones: List[Dict[str, Any]], ruta_salida: str) -> None:
    """
    Guarda las combinaciones generadas en un archivo JSON
    
    Args:
        combinaciones: Lista de combinaciones generadas
        ruta_salida: Ruta donde se guardará el archivo de salida
    """
    try:
        with open(ruta_salida, 'w', encoding='utf-8') as f:
            json.dump(combinaciones, f, ensure_ascii=False, indent=2)
        print(f"Combinaciones guardadas exitosamente en {ruta_salida}")
    except Exception as e:
        print(f"Error al guardar las combinaciones: {e}")

def generar_historia_usuario(combinacion: Dict[str, Any], indice: int) -> str:
    """
    Genera una historia de usuario basada en la combinación de valores proporcionada
    
    Args:
        combinacion: Diccionario con los valores para cada punto clave
        indice: Índice de la historia para identificación
        
    Returns:
        Historia de usuario generada
    """
    try:
        # Crear un prompt para el modelo de lenguaje
        prompt = f"""
Genera una historia de usuario detallada para el sector inmobiliario basada en los siguientes puntos clave:

"""
        # Añadir cada punto clave y su valor al prompt
        for llave, valor in combinacion.items():
            if valor:  # Solo incluir si tiene un valor
                # Formatear la llave para que sea más legible (reemplazar _ por espacios)
                llave_formateada = llave.replace('_', ' ').title()
                prompt += f"- {llave_formateada}: {valor}\n"
        
        prompt += """
Crea una narrativa coherente y detallada que integre estos elementos. La historia debe ser realista y útil para entender las necesidades y comportamientos de los usuarios en el sector inmobiliario.

Estructura sugerida (pero puedes adaptarla):
1. Perfil del usuario
2. Situación actual y motivación
3. Necesidades y criterios de búsqueda
4. Proceso de búsqueda y toma de decisiones
5. Obstáculos y preocupaciones
6. Expectativas del servicio inmobiliario
"""
        
        # Crear mensajes para el modelo
        mensajes = [
            SystemMessage(content=SYSTEM_MESSAGE),
            HumanMessage(content=prompt)
        ]
        
        # Generar la historia
        print(f"Generando historia de usuario #{indice}...")
        response = llm.invoke(mensajes)
        
        return response.content
    
    except Exception as e:
        print(f"Error al generar historia de usuario: {e}")
        return f"Error al generar historia: {str(e)}"

def guardar_historia(historia: str, directorio_salida: str, indice: int) -> str:
    """
    Guarda una historia de usuario en un archivo individual
    
    Args:
        historia: Contenido de la historia de usuario
        directorio_salida: Directorio donde se guardarán las historias
        indice: Índice de la historia
        
    Returns:
        Ruta del archivo donde se guardó la historia
    """
    try:
        # Crear el directorio si no existe
        os.makedirs(directorio_salida, exist_ok=True)
        
        # Generar un nombre de archivo único
        nombre_archivo = f"historia_usuario_{indice}_{uuid.uuid4().hex[:8]}.txt"
        ruta_archivo = os.path.join(directorio_salida, nombre_archivo)
        
        # Guardar la historia en el archivo
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            f.write(historia)
        
        print(f"Historia guardada en {ruta_archivo}")
        return ruta_archivo
    
    except Exception as e:
        print(f"Error al guardar historia: {e}")
        return ""

def main():
    # Rutas de los archivos
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_resumen = os.path.join(directorio_actual, "resumen.json")
    ruta_dic = os.path.join(directorio_actual, "dic.json")
    ruta_salida_combinaciones = os.path.join(directorio_actual, "historias_generadas.json")
    directorio_historias = os.path.join(directorio_actual, "historias")
    
    # Solicitar al usuario la cantidad de combinaciones/historias a generar
    try:
        cantidad = int(input("Ingrese la cantidad de historias de usuario a generar: "))
    except ValueError:
        print("Valor inválido. Se generarán 5 historias por defecto.")
        cantidad = 5
    
    # Cargar las llaves primarias y el diccionario de valores
    llaves_primarias = cargar_llaves_primarias(ruta_resumen)
    diccionario_valores = cargar_diccionario_valores(ruta_dic)
    
    if not llaves_primarias:
        print("No se encontraron llaves primarias. Verifique el archivo resumen.json")
        return
    
    if not diccionario_valores:
        print("No se encontraron valores en el diccionario. Verifique el archivo dic.json")
        return
    
    print(f"Se encontraron {len(llaves_primarias)} llaves primarias")
    
    # Generar las combinaciones aleatorias
    combinaciones = generar_combinaciones_aleatorias(llaves_primarias, diccionario_valores, cantidad)
    
    # Guardar las combinaciones en un archivo JSON
    guardar_combinaciones(combinaciones, ruta_salida_combinaciones)
    
    print(f"Se generaron {len(combinaciones)} combinaciones aleatorias")
    
    # Generar y guardar las historias de usuario
    rutas_historias = []
    for i, combinacion in enumerate(combinaciones, 1):
        # Generar la historia
        historia = generar_historia_usuario(combinacion, i)
        
        # Guardar la historia en un archivo individual
        ruta_historia = guardar_historia(historia, directorio_historias, i)
        if ruta_historia:
            rutas_historias.append(ruta_historia)
    
    print(f"\nResumen de la generación:")
    print(f"- Combinaciones generadas: {len(combinaciones)}")
    print(f"- Historias de usuario creadas: {len(rutas_historias)}")
    print(f"- Directorio de historias: {directorio_historias}")

if __name__ == "__main__":
    main()
