# CRM Inmobiliario con Inteligencia Artificial

## Descripción General

Este sistema es un CRM (Customer Relationship Management) especializado para el sector inmobiliario, que integra funcionalidades avanzadas de inteligencia artificial para mejorar la gestión de propiedades, clientes y procesos de venta/alquiler. La plataforma permite a los agentes inmobiliarios administrar de manera eficiente todo el ciclo de vida de las propiedades y las relaciones con los clientes.

## Características Principales

### Gestión de Propiedades

- **Registro completo de propiedades**: Información detallada sobre tipo, área, habitaciones, baños, nivel, etc.
- **Modalidades de negocio**: Soporte para venta y/o alquiler con diferentes precios y condiciones.
- **Multimedia**: Gestión de fotos y videos de las propiedades.
- **Ubicación geográfica**: Organización jerárquica por localidad, zona, barrio y edificio.
- **Amenidades y características**: Registro de características interiores y amenidades disponibles.
- **Puntos y zonas de interés**: Vinculación con lugares relevantes cercanos a la propiedad.

### Gestión de Requerimientos

- **Registro de necesidades de clientes**: Captura detallada de lo que buscan los clientes.
- **Presupuestos**: Manejo de rangos de presupuesto para compra o alquiler.
- **Especificaciones técnicas**: Área, habitaciones, baños, parqueaderos, etc.
- **Preferencias de ubicación**: Localidades, zonas y barrios de interés.
- **Priorización**: Clasificación por importancia y urgencia.
- **Seguimiento**: Control del estado de los requerimientos (pendiente, en proceso, completado).

### Gestión de Tareas

- **Planificación de actividades**: Llamadas de seguimiento, visitas a inmuebles, documentación, etc.
- **Asignación a agentes**: Distribución de responsabilidades entre el equipo.
- **Priorización**: Clasificación por nivel de importancia (baja, media, alta).
- **Estados de seguimiento**: Control del progreso (pendiente, en proceso, completada, cancelada).
- **Documentación**: Adjuntar archivos relevantes a cada fase de seguimiento.

### Funcionalidades de IA

- **Generación de descripciones**: Creación automática de descripciones profesionales y atractivas para propiedades.
- **Análisis de imágenes**: Reconocimiento y descripción de espacios a partir de fotografías.
- **Transcripción de voz**: Conversión de notas de voz a texto para facilitar el registro de información.
- **Generación de imágenes**: Creación de visuales para marketing inmobiliario.
- **Asistente conversacional**: Chatbot especializado con conocimiento contextual sobre propiedades, edificios y localidades.

### Organización Geográfica

- **Localidades**: División administrativa principal.
- **Zonas**: Áreas específicas dentro de las localidades.
- **Barrios**: Subdivisiones residenciales con características propias.
- **Edificios**: Construcciones específicas con sus propias amenidades y características.
- **Puntos de interés**: Lugares relevantes (comercios, parques, servicios, etc.).

## Arquitectura Técnica

### Backend

- **Framework**: Django con Django REST Framework
- **Base de datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Integración IA**: OpenAI (GPT-4, DALL-E, Whisper)
- **Almacenamiento multimedia**: Sistema de archivos con Django FileField

### Modelos Principales

- **Propiedad**: Núcleo del sistema, contiene toda la información de los inmuebles.
- **Requerimiento**: Registro de necesidades de los clientes.
- **Tarea**: Actividades de seguimiento asignadas a los agentes.
- **Edificio**: Información sobre construcciones específicas.
- **Localidad/Zona/Barrio**: Jerarquía geográfica.
- **Multimedia**: Gestión de archivos asociados a diferentes entidades.
- **Amenidades/Características**: Catálogos de facilidades y características.

## Casos de Uso Principales

1. **Registro y gestión de propiedades**
2. **Captura de requerimientos de clientes**
3. **Matching entre propiedades y requerimientos**
4. **Seguimiento de procesos de venta/alquiler**
5. **Generación automática de contenido con IA**
6. **Análisis de imágenes de propiedades**
7. **Gestión de tareas y seguimiento de agentes**

## Requisitos Técnicos

- Python 3.8+
- Django 3.2+
- OpenAI API Key
- Espacio de almacenamiento para multimedia
- Dependencias adicionales en requirements.txt

## Instalación y Configuración

1. Clonar el repositorio
2. Crear entorno virtual: `python -m venv venv`
3. Activar entorno virtual: `source venv/bin/activate` (Linux/Mac) o `venv\Scripts\activate` (Windows)
4. Instalar dependencias: `pip install -r requirements.txt`
5. Configurar variables de entorno (crear archivo .env con OPENAI_API_KEY)
6. Ejecutar migraciones: `python manage.py migrate`
7. Crear superusuario: `python manage.py createsuperuser`
8. Iniciar servidor: `python manage.py runserver`

## Contribución

Para contribuir al proyecto:

1. Hacer fork del repositorio
2. Crear una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Hacer commit de tus cambios (`git commit -m 'Añadir nueva funcionalidad'`)
4. Hacer push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir un Pull Request
