# Modelos y Relaciones del Sistema CRM Inmobiliario

Este documento describe en detalle todos los modelos de datos que componen el sistema CRM inmobiliario y las relaciones entre ellos.

## Módulo de Cuentas (accounts)

### AgenteModel
Representa a los agentes inmobiliarios que utilizan el sistema.

**Campos principales:**
- `user`: Relación OneToOne con el modelo User de Django (nombre, apellido, email, etc.)
- `role`: Rol del agente ('user', 'admin')
- `fecha_ingreso`: Fecha de registro en el sistema
- `telefono`: Número de contacto
- `cedula`: Documento de identidad (único)
- `zona_especializacion`: Área geográfica de especialización
- `estado`: Estado del agente ('activo', 'inactivo')

**Relaciones:**
- `User` (Django): OneToOne
- `ClienteModel`: OneToMany (un agente puede tener muchos clientes)
- `PropiedadModel`: OneToMany (un agente puede gestionar muchas propiedades)
- `RequerimientoModel`: OneToMany (un agente puede gestionar muchos requerimientos)
- `TareaModel`: OneToMany (un agente puede tener muchas tareas asignadas)

### ClienteModel
Representa a los clientes que buscan propiedades o son propietarios.

**Campos principales:**
- `agente`: Agente asignado al cliente
- `fecha_ingreso`: Fecha de registro
- `nombre`: Nombre del cliente
- `apellidos`: Apellidos del cliente
- `telefono`: Número principal de contacto
- `telefono_secundario`: Número alternativo
- `correo`: Email de contacto
- `cedula`: Documento de identidad
- `password`: Contraseña para acceso al sistema
- `canal_ingreso`: Cómo llegó el cliente al sistema
- `estado_del_cliente`: Estado ('activo', 'inactivo')
- `notas`: Observaciones adicionales

**Relaciones:**
- `AgenteModel`: ManyToOne (muchos clientes pueden tener un mismo agente)
- `PropiedadModel`: OneToMany (un cliente puede ser propietario de varias propiedades)
- `RequerimientoModel`: OneToMany (un cliente puede tener varios requerimientos)
- `TareaModel`: OneToMany (relacionado con tareas de seguimiento)

## Módulo CRM (crm)

### PropiedadModel
Modelo central que representa las propiedades inmobiliarias.

**Campos principales:**
- `agente`: Agente que gestiona la propiedad
- `propietario`: Cliente propietario
- `titulo`: Título descriptivo
- `modalidad_de_negocio`: JSON con información de venta/alquiler
- `tipo_propiedad`: Tipo de inmueble (apartamento, casa, etc.)
- `edificio`: Edificio al que pertenece (si aplica)
- `descripcion`: Descripción detallada
- `direccion`: JSON con datos de ubicación
- `nivel`: Piso o nivel
- `metro_cuadrado_construido`: Área construida
- `metro_cuadrado_propiedad`: Área total
- `habitaciones`: Número de habitaciones
- `habitacion_de_servicio`: Habitaciones de servicio
- `banos`: Número de baños
- `terraza`: Información sobre terraza
- `balcon`: Información sobre balcón
- `garajes`: JSON con información de parqueaderos
- `depositos`: JSON con información de depósitos
- `mascotas`: Si permite mascotas ('si', 'no')
- `estrato`: Estrato socioeconómico
- `valor_predial`: Valor del impuesto predial
- `valor_administracion`: Valor de la administración
- `ano_construccion`: Año de construcción
- `codigo`: Código único de la propiedad
- `notas`: Observaciones adicionales
- `honorarios`: JSON con información de honorarios

**Relaciones:**
- `AgenteModel`: ManyToOne
- `ClienteModel`: ManyToOne
- `EdificioModel`: ManyToOne
- `CaracteristicasInterioresModel`: ManyToOne
- `AmenidadesModel`: ManyToMany
- `PuntoDeInteresModel`: ManyToOne
- `ZonasDeInteresModel`: ManyToOne
- `MultimediaModel`: OneToMany (relación genérica)

### EdificioModel
Representa edificios o conjuntos residenciales.

**Campos principales:**
- `nombre`: Nombre del edificio
- `contacto_administrador`: Información del administrador
- `sigla`: Abreviatura para códigos
- `desarrollador`: Empresa constructora
- `estado`: Estado del edificio
- `tipo_edificio`: Tipo de edificación
- `barrio`: Barrio donde se ubica
- `direccion`: Dirección física
- `estrato`: Estrato socioeconómico
- `telefono`: Teléfono de contacto
- `unidades`: JSON con información de unidades disponibles
- `torres`: Número de torres
- `parqueaderos`: Número de parqueaderos
- `descripcion`: Descripción detallada
- `ubicacion`: JSON con coordenadas
- `ano_construccion`: Año de construcción
- `servicios_adicionales`: Servicios que ofrece

**Relaciones:**
- `ContactoAdministradorModel`: ManyToOne
- `BarrioModel`: ManyToOne
- `AmenidadesModel`: ManyToMany
- `PuntoDeInteresModel`: ManyToOne
- `ZonasDeInteresModel`: ManyToOne
- `MultimediaModel`: OneToMany (relación genérica)
- `PropiedadModel`: OneToMany

### LocalidadModel
Representa divisiones administrativas principales (como municipios o distritos).

**Campos principales:**
- `nombre`: Nombre de la localidad
- `sigla`: Abreviatura para códigos
- `descripcion`: Descripción detallada

**Relaciones:**
- `PuntoDeInteresModel`: ManyToOne
- `ZonasDeInteresModel`: ManyToOne
- `MultimediaModel`: OneToMany (relación genérica)
- `BarrioModel`: OneToMany
- `RequerimientoModel`: OneToMany

### ZonaModel
Representa áreas específicas dentro de las localidades.

**Campos principales:**
- `nombre`: Nombre de la zona
- `sigla`: Abreviatura para códigos
- `descripcion`: Descripción detallada
- `tipo_zona`: Tipo de zona

**Relaciones:**
- `BarrioModel`: ManyToMany
- `RequerimientoModel`: OneToMany

### BarrioModel
Representa barrios o vecindarios.

**Campos principales:**
- `nombre`: Nombre del barrio
- `sigla`: Abreviatura para códigos
- `descripcion`: Descripción detallada
- `localidad`: Localidad a la que pertenece
- `estrato_predominante`: Estrato socioeconómico predominante
- `tipo_barrio`: Tipo de barrio (residencial, comercial, etc.)

**Relaciones:**
- `LocalidadModel`: ManyToOne
- `PuntoDeInteresModel`: ManyToOne
- `ZonasDeInteresModel`: ManyToOne
- `MultimediaModel`: OneToMany (relación genérica)
- `ZonaModel`: ManyToMany
- `EdificioModel`: OneToMany
- `RequerimientoModel`: OneToMany

### AmenidadesModel
Representa comodidades o facilidades disponibles en propiedades o edificios.

**Campos principales:**
- `nombre`: Nombre de la amenidad
- `categoria`: Categoría (piscina, gimnasio, etc.)
- `descripcion`: Descripción detallada
- `icono`: Imagen representativa

**Relaciones:**
- `PropiedadModel`: ManyToMany
- `EdificioModel`: ManyToMany

### CaracteristicasInterioresModel
Representa características específicas del interior de las propiedades.

**Campos principales:**
- `caracteristica`: Nombre de la característica
- `categoria`: Categoría
- `tipo_propiedad`: Tipo de propiedad aplicable
- `descripcion`: Descripción detallada
- `icono`: Imagen representativa

**Relaciones:**
- `PropiedadModel`: OneToMany

### ZonasDeInteresModel
Representa áreas de interés cercanas a propiedades.

**Campos principales:**
- `nombre`: Nombre de la zona
- `categoria`: Categoría
- `descripcion`: Descripción detallada
- `ubicacion`: JSON con coordenadas
- `icono`: Imagen representativa

**Relaciones:**
- `MultimediaModel`: OneToMany (relación genérica)
- `PuntoDeInteresModel`: ManyToMany
- `PropiedadModel`: OneToMany
- `EdificioModel`: OneToMany
- `LocalidadModel`: OneToMany
- `BarrioModel`: OneToMany

### PuntoDeInteresModel
Representa lugares específicos de interés (comercios, parques, etc.).

**Campos principales:**
- `nombre`: Nombre del punto de interés
- `categoria`: Categoría
- `descripcion`: Descripción detallada
- `ubicacion`: JSON con coordenadas
- `direccion`: Dirección física
- `icono`: Imagen representativa

**Relaciones:**
- `MultimediaModel`: OneToMany (relación genérica)
- `ZonasDeInteresModel`: ManyToMany
- `PropiedadModel`: OneToMany
- `EdificioModel`: OneToMany
- `LocalidadModel`: OneToMany
- `BarrioModel`: OneToMany

### RequerimientoModel
Representa las necesidades de búsqueda de propiedades de los clientes.

**Campos principales:**
- `agente`: Agente asignado
- `cliente`: Cliente que hace el requerimiento
- `fecha_ingreso`: Fecha de registro
- `tiempo_estadia`: Tiempo de estadía (para alquileres)
- `tipo_negocio`: JSON con tipo de negocio (compra/alquiler)
- `presupuesto_minimo`: Presupuesto mínimo
- `presupuesto_maximo`: Presupuesto máximo
- `presupuesto_minimo_compra`: Presupuesto mínimo para compra
- `presupuesto_maximo_compra`: Presupuesto máximo para compra
- `habitantes`: Número de habitantes
- `area_minima`: Área mínima requerida
- `area_maxima`: Área máxima requerida
- `area_lote`: Área de lote requerida
- `habitaciones`: Número de habitaciones
- `habitaciones_servicio`: Habitaciones de servicio
- `banos`: Número de baños
- `parqueaderos`: Número de parqueaderos
- `depositos`: Número de depósitos
- `mascotas`: Si tiene mascotas ('si', 'no')
- `descripcion`: Descripción detallada
- `estado`: Estado del requerimiento
- `edificacion`: JSON con tipos de edificación preferidos
- `prioridad`: Nivel de prioridad
- `fecha_ideal_entrega`: Fecha ideal para entrega
- `negocibles`: Aspectos negociables
- `no_negocibles`: Aspectos no negociables
- `comentarios`: JSON con comentarios adicionales

**Relaciones:**
- `AgenteModel`: ManyToOne
- `ClienteModel`: ManyToOne
- `LocalidadModel`: ManyToOne
- `ZonaModel`: ManyToOne
- `BarrioModel`: ManyToOne
- `EdificioModel`: ManyToOne

### TareaModel
Representa actividades de seguimiento asignadas a los agentes.

**Campos principales:**
- `fecha_creacion`: Fecha de creación
- `fecha_vencimiento`: Fecha límite
- `tipo_tarea`: Tipo de tarea
- `prioridad`: Nivel de prioridad
- `estado`: Estado de la tarea
- `descripcion`: Descripción detallada
- `agente`: Agente asignado
- `cliente`: Cliente relacionado
- `propiedad`: Propiedad relacionada (opcional)

**Relaciones:**
- `AgenteModel`: ManyToOne
- `ClienteModel`: ManyToOne
- `PropiedadModel`: ManyToOne
- `FaseSeguimientoModel`: OneToMany

### FaseSeguimientoModel
Representa etapas de seguimiento de las tareas.

**Campos principales:**
- `tarea`: Tarea relacionada
- `fecha_inicio`: Fecha de inicio
- `fecha_fin`: Fecha de finalización
- `descripcion`: Descripción detallada
- `agente_responsable`: Agente responsable
- `estado`: Estado de la fase
- `archivos_adjuntos`: Documentos adjuntos
- `notas_internas`: Notas para uso interno
- `resultado`: Resultado de la fase

**Relaciones:**
- `TareaModel`: ManyToOne
- `AgenteModel`: ManyToOne

### MultimediaModel
Modelo genérico para gestionar archivos multimedia asociados a diferentes entidades.

**Campos principales:**
- `content_type`: Tipo de contenido (relación genérica)
- `object_id`: ID del objeto relacionado
- `tipo`: Tipo de multimedia (foto, video)
- `archivo`: Archivo multimedia
- `titulo`: Título descriptivo
- `descripcion`: Descripción detallada
- `es_principal`: Si es la imagen principal
- `fecha_subida`: Fecha de carga

**Relaciones genéricas con:**
- `PropiedadModel`
- `EdificioModel`
- `LocalidadModel`
- `BarrioModel`
- `ZonasDeInteresModel`
- `PuntoDeInteresModel`

### AIQueryModel
Registra consultas realizadas a servicios de IA.

**Campos principales:**
- `query_type`: Tipo de consulta
- `model_type`: Modelo de IA utilizado
- `input_data`: Datos de entrada (JSON)
- `output_data`: Datos de salida (JSON)
- `created_at`: Fecha de creación
- `status`: Estado de la consulta
- `error_message`: Mensaje de error (si existe)

## Módulo de Chat (chat)

### ChatRoomModel
Representa salas de chat para comunicación.

**Campos principales:**
- `name`: Nombre de la sala
- `participants`: Participantes

**Relaciones:**
- `User` (Django): ManyToMany
- `MessageModel`: OneToMany

### MessageModel
Representa mensajes individuales en las conversaciones.

**Campos principales:**
- `room`: Sala de chat
- `sender`: Remitente
- `content`: Contenido del mensaje
- `timestamp`: Fecha y hora

**Relaciones:**
- `ChatRoomModel`: ManyToOne
- `User` (Django): ManyToOne

### ConversationHistory
Almacena el historial de conversaciones con el asistente de IA.

**Campos principales:**
- `user_id`: ID del usuario
- `messages`: JSON con mensajes
- `created_at`: Fecha de creación

## Diagrama de Relaciones

```
+----------------+       +----------------+       +----------------+
| AgenteModel    |<------| ClienteModel   |<------| RequerimientoM |
+----------------+       +----------------+       +----------------+
        ^                        ^                        |
        |                        |                        |
        v                        v                        v
+----------------+       +----------------+       +----------------+
| PropiedadModel |<------| TareaModel     |<------| FaseSeguimient |
+----------------+       +----------------+       +----------------+
        ^                        ^
        |                        |
        v                        v
+----------------+       +----------------+       +----------------+
| EdificioModel  |<------| BarrioModel    |<------| LocalidadModel|
+----------------+       +----------------+       +----------------+
        ^                        ^                        ^
        |                        |                        |
        v                        v                        v
+----------------+       +----------------+       +----------------+
| AmenidadesMode |       | ZonaModel      |       | MultimediaMode|
+----------------+       +----------------+       +----------------+
        ^                        ^                        ^
        |                        |                        |
        v                        v                        v
+----------------+       +----------------+       +----------------+
| CaracteristicaI|       | ZonasDeInteres |<------| PuntoDeInteres|
+----------------+       +----------------+       +----------------+
```

## Relaciones Clave

1. **Agente-Cliente**: Un agente puede tener muchos clientes, pero un cliente tiene un solo agente asignado.

2. **Propiedad-Agente-Cliente**: Una propiedad tiene un agente que la gestiona y un cliente que es el propietario.

3. **Requerimiento-Cliente**: Un cliente puede tener múltiples requerimientos de búsqueda.

4. **Tarea-Agente-Cliente**: Las tareas se asignan a un agente y están relacionadas con un cliente específico.

5. **Jerarquía Geográfica**: Localidad > Zona > Barrio > Edificio > Propiedad, representando la organización territorial.

6. **Multimedia Genérica**: El modelo MultimediaModel utiliza relaciones genéricas para asociar archivos multimedia con diferentes entidades.

7. **Amenidades y Características**: Tanto propiedades como edificios pueden tener múltiples amenidades asociadas.

8. **Puntos y Zonas de Interés**: Propiedades, edificios, localidades y barrios pueden tener puntos y zonas de interés cercanos.

9. **Seguimiento de Tareas**: Las tareas tienen fases de seguimiento que registran el progreso y los resultados.

10. **Chat y Comunicación**: El sistema permite la comunicación entre usuarios a través de salas de chat y mensajes.

Esta estructura de modelos permite una gestión completa del ciclo inmobiliario, desde el registro de propiedades hasta el seguimiento de clientes y tareas, con integración de funcionalidades de IA para mejorar la experiencia del usuario. 