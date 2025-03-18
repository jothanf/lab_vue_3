import os
import sys
import django
import random
from faker import Faker
from django.db import models

# Configurar entorno Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'igh.settings')
django.setup()

# Importar modelos después de configurar Django
from django.contrib.auth.models import User
from accounts.models import AgenteModel, ClienteModel
from crm.models import (
    AmenidadesModel, 
    CaracteristicasInterioresModel, 
    LocalidadModel, 
    BarrioModel,
    ZonaModel,
    EdificioModel,
    ZonasDeInteresModel,
    PuntoDeInteresModel,
    ContactoAdministradorModel,
    PropiedadModel,
    RequerimientoModel,
    TareaModel
)

# Inicializar Faker para generar datos ficticios
fake = Faker('es_ES')  # Usar locale español

def create_user(username, first_name, last_name, email, password, is_staff=False):
    """Crear un usuario de Django"""
    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_staff=is_staff
        )
        print(f"Usuario creado: {username}")
        return user
    except Exception as e:
        print(f"Error al crear usuario {username}: {str(e)}")
        return None

def create_agente(user, telefono, cedula=None, role='user'):
    """Crear un agente inmobiliario"""
    try:
        # Si no se proporciona una cédula, generar una aleatoria
        if not cedula:
            cedula = ''.join([str(random.randint(0, 9)) for _ in range(10)])
        
        # Verificar si ya existe un agente con esta cédula
        if AgenteModel.objects.filter(cedula=cedula).exists():
            print(f"Ya existe un agente con la cédula {cedula}. Generando una nueva cédula...")
            # Generar una nueva cédula aleatoria
            while AgenteModel.objects.filter(cedula=cedula).exists():
                cedula = ''.join([str(random.randint(0, 9)) for _ in range(10)])
            print(f"Nueva cédula generada: {cedula}")
        
        agente = AgenteModel.objects.create(
            user=user,
            telefono=telefono,
            cedula=cedula,
            role=role,
            estado='activo'
        )
        print(f"Agente creado: {user.first_name} {user.last_name} con cédula {cedula}")
        return agente
    except Exception as e:
        print(f"Error al crear agente para {user.username}: {str(e)}")
        # Imprimir información adicional para depuración
        import traceback
        traceback.print_exc()
        return None

def create_cliente(agente, nombre, apellidos, telefono, correo, cedula=None):
    """Crear un cliente asociado a un agente"""
    try:
        cliente = ClienteModel.objects.create(
            agente=agente,
            nombre=nombre,
            apellidos=apellidos,
            telefono=telefono,
            correo=correo,
            cedula=cedula,
            estado_del_cliente='activo'
        )
        print(f"Cliente creado: {nombre} {apellidos}")
        return cliente
    except Exception as e:
        print(f"Error al crear cliente {nombre} {apellidos}: {str(e)}")
        return None

def create_amenidad(nombre, categoria, descripcion=None):
    """Crear una amenidad"""
    try:
        amenidad = AmenidadesModel.objects.create(
            nombre=nombre,
            categoria=categoria,
            descripcion=descripcion or f"Descripción de {nombre}"
        )
        print(f"Amenidad creada: {nombre}")
        return amenidad
    except Exception as e:
        print(f"Error al crear amenidad {nombre}: {str(e)}")
        return None

def create_caracteristica_interior(caracteristica, categoria, tipo_propiedad=None, descripcion=None):
    """Crear una característica interior"""
    try:
        caract = CaracteristicasInterioresModel.objects.create(
            caracteristica=caracteristica,
            categoria=categoria,
            tipo_propiedad=tipo_propiedad,
            descripcion=descripcion or f"Descripción de {caracteristica}"
        )
        print(f"Característica interior creada: {caracteristica}")
        return caract
    except Exception as e:
        print(f"Error al crear característica interior {caracteristica}: {str(e)}")
        return None

def create_localidad(nombre, sigla=None, descripcion=None):
    """Crear una localidad"""
    try:
        localidad = LocalidadModel.objects.create(
            nombre=nombre,
            sigla=sigla or nombre[:3].upper(),
            descripcion=descripcion or f"Localidad de {nombre}"
        )
        print(f"Localidad creada: {nombre}")
        return localidad
    except Exception as e:
        print(f"Error al crear localidad {nombre}: {str(e)}")
        return None

def create_barrio(nombre, localidad, sigla=None, descripcion=None, estrato_predominante=None, tipo_barrio='residencial'):
    """Crear un barrio"""
    try:
        barrio = BarrioModel.objects.create(
            nombre=nombre,
            localidad=localidad,
            sigla=sigla or nombre[:3].upper(),
            descripcion=descripcion or f"Barrio {nombre} en {localidad.nombre}",
            estrato_predominante=estrato_predominante or random.randint(1, 6),
            tipo_barrio=tipo_barrio
        )
        print(f"Barrio creado: {nombre} en {localidad.nombre}")
        return barrio
    except Exception as e:
        print(f"Error al crear barrio {nombre}: {str(e)}")
        return None

def create_zona(nombre, sigla=None, descripcion=None, tipo_zona='residencial'):
    """Crear una zona"""
    try:
        zona = ZonaModel.objects.create(
            nombre=nombre,
            sigla=sigla or nombre[:3].upper(),
            descripcion=descripcion or f"Zona {nombre}",
            tipo_zona=tipo_zona
        )
        print(f"Zona creada: {nombre}")
        return zona
    except Exception as e:
        print(f"Error al crear zona {nombre}: {str(e)}")
        return None

def create_punto_de_interes(nombre, categoria, descripcion=None, direccion=None, ubicacion=None):
    """Crear un punto de interés"""
    try:
        punto = PuntoDeInteresModel.objects.create(
            nombre=nombre,
            categoria=categoria,
            descripcion=descripcion or f"Punto de interés: {nombre}",
            direccion=direccion or fake.address(),
            ubicacion=ubicacion or {"latitud": str(fake.latitude()), "longitud": str(fake.longitude())}
        )
        print(f"Punto de interés creado: {nombre}")
        return punto
    except Exception as e:
        print(f"Error al crear punto de interés {nombre}: {str(e)}")
        return None

def create_zona_de_interes(nombre, categoria, descripcion=None, ubicacion=None):
    """Crear una zona de interés"""
    try:
        zona = ZonasDeInteresModel.objects.create(
            nombre=nombre,
            categoria=categoria,
            descripcion=descripcion or f"Zona de interés: {nombre}",
            ubicacion=ubicacion or {"latitud": str(fake.latitude()), "longitud": str(fake.longitude())}
        )
        print(f"Zona de interés creada: {nombre}")
        return zona
    except Exception as e:
        print(f"Error al crear zona de interés {nombre}: {str(e)}")
        return None

def create_contacto_administrador(nombre, telefono, correo):
    """Crear un contacto de administrador para edificios"""
    try:
        contacto = ContactoAdministradorModel.objects.create(
            nombre=nombre,
            telefono=telefono,
            correo=correo
        )
        print(f"Contacto administrador creado: {nombre}")
        return contacto
    except Exception as e:
        print(f"Error al crear contacto administrador {nombre}: {str(e)}")
        return None

def create_edificio(nombre, barrio, contacto_administrador=None, sigla=None, descripcion=None, 
                   estado='Entregado', tipo_edificio='Edificio Residencial', estrato=None, 
                   direccion=None, torres=1, parqueaderos=0):
    """Crear un edificio"""
    try:
        edificio = EdificioModel.objects.create(
            nombre=nombre,
            barrio=barrio,
            contacto_administrador=contacto_administrador,
            sigla=sigla or nombre[:3].upper(),
            descripcion=descripcion or f"Edificio {nombre} en {barrio.nombre}",
            estado=estado,
            tipo_edificio=tipo_edificio,
            estrato=estrato or barrio.estrato_predominante,
            direccion=direccion or fake.street_address(),
            torres=torres,
            parqueaderos=parqueaderos,
            ubicacion={"latitud": str(fake.latitude()), "longitud": str(fake.longitude())},
            ano_construccion=random.randint(2000, 2023),
            servicios_adicionales="Portería 24 horas, CCTV, Ascensor"
        )
        print(f"Edificio creado: {nombre} en {barrio.nombre}")
        return edificio
    except Exception as e:
        print(f"Error al crear edificio {nombre}: {str(e)}")
        return None

def create_propiedad(agente, propietario, titulo, tipo_propiedad, edificio=None, barrio=None, 
                    habitaciones=0, banos=0, metro_cuadrado_construido=0, estrato=None, 
                    valor_administracion=0, amenidades=None):
    """Crear una propiedad inmobiliaria"""
    try:
        # Crear dirección ficticia
        direccion = {
            "direccion": fake.street_address(),
            "datos_adicionales": {
                "interior": str(random.randint(1, 10)),
                "torre": random.choice(["A", "B", "C", "D"]),
                "apartamento": str(random.randint(101, 1001))
            },
            "coordenada_1": str(fake.latitude()),
            "coordenada_2": str(fake.longitude())
        }
        
        # Crear información de garajes
        garajes = {
            "cantidad": str(random.randint(0, 3)),
            "id": ''.join([str(random.randint(0, 9)) for _ in range(10)])
        }
        
        # Crear información de depósitos
        depositos = {
            "cantidad": str(random.randint(0, 2)),
            "id": ''.join([str(random.randint(0, 9)) for _ in range(10)])
        }
        
        # Crear modalidad de negocio
        modalidades = ["venta", "arriendo", "permuta"]
        modalidad_de_negocio = random.choice(modalidades)
        
        # Crear propiedad
        propiedad = PropiedadModel.objects.create(
            agente=agente,
            propietario=propietario,
            titulo=titulo,
            modalidad_de_negocio=modalidad_de_negocio,
            tipo_propiedad=tipo_propiedad,
            edificio=edificio,
            descripcion=f"Propiedad {tipo_propiedad} en {edificio.nombre if edificio else barrio.nombre if barrio else 'ubicación desconocida'}. {fake.paragraph()}",
            direccion=direccion,
            nivel=random.randint(1, 20) if tipo_propiedad == 'apartamento' else 1,
            metro_cuadrado_construido=metro_cuadrado_construido,
            metro_cuadrado_propiedad=metro_cuadrado_construido + random.randint(0, 50),
            habitaciones=habitaciones,
            habitacion_de_servicio=1 if random.random() > 0.7 else 0,
            banos=banos,
            terraza='si' if random.random() > 0.7 else 'no',
            balcon='si' if random.random() > 0.6 else 'no',
            garajes=garajes,
            depositos=depositos,
            mascotas='si' if random.random() > 0.5 else 'no',
            estrato=estrato,
            valor_predial=random.randint(500000, 5000000),
            valor_administracion=valor_administracion,
            ano_construccion=random.randint(1990, 2023),
            notas=[{"nota": fake.paragraph(), "fecha": fake.date_this_decade().isoformat()}],
            honorarios={"porcentaje": random.randint(3, 10), "valor_fijo": random.randint(1000000, 5000000)}
        )
        
        # Asignar amenidades si se proporcionan
        if amenidades:
            for amenidad in amenidades:
                propiedad.amenidades.add(amenidad)
        
        print(f"Propiedad creada: {titulo}")
        return propiedad
    except Exception as e:
        print(f"Error al crear propiedad {titulo}: {str(e)}")
        return None

def create_requerimiento(agente, cliente, tipo_negocio, presupuesto_min, presupuesto_max, 
                        habitaciones, banos, area_minima, area_maxima, localidad=None, 
                        barrio=None, zona=None, edificio=None):
    """Crear un requerimiento de cliente"""
    try:
        # Crear cercanías
        cercanias_opciones = ["parque", "centro comercial", "colegio", "universidad", "hospital", "transporte público"]
        cercanias = random.sample(cercanias_opciones, random.randint(1, 3))
        
        # Crear edificación
        tipos_edificacion = ["centro_comercial", "centro_empresarial", "condominio_campestre", 
                           "edificio_independiente", "independiente", "parcelacion", 
                           "unidad_cerrada", "unidad_cerrada_con_zonas_comunes"]
        edificacion = {
            "tipos": random.sample(tipos_edificacion, random.randint(1, 3))
        }
        
        # Crear información legal financiera
        info_legal = {
            "certificado_libertad": "si" if random.random() > 0.5 else "no",
            "hipoteca": "si" if random.random() > 0.7 else "no"
        }
        
        # Crear honorarios
        honorarios = {
            "porcentaje": random.randint(3, 10),
            "valor_fijo": random.randint(1000000, 5000000)
        }
        
        # Crear comentarios
        comentarios = [
            {"comentario": fake.paragraph(), "fecha": fake.date_this_year().isoformat(), "autor": agente.user.username}
        ]
        
        # Crear requerimiento
        requerimiento = RequerimientoModel.objects.create(
            agente=agente,
            cliente=cliente,
            tiempo_estadia=random.randint(6, 36) if "arriendo" in tipo_negocio else None,
            tipo_negocio=tipo_negocio,
            presupuesto_minimo=presupuesto_min if "arriendo" in tipo_negocio else None,
            presupuesto_maximo=presupuesto_max if "arriendo" in tipo_negocio else None,
            presupuesto_minimo_compra=presupuesto_min if "venta" in tipo_negocio else None,
            presupuesto_maximo_compra=presupuesto_max if "venta" in tipo_negocio else None,
            habitantes=random.randint(1, 6),
            area_minima=area_minima,
            area_maxima=area_maxima,
            habitaciones=habitaciones,
            habitaciones_servicio=1 if random.random() > 0.7 else 0,
            banos=banos,
            parqueaderos=random.randint(0, 3),
            depositos=random.randint(0, 2),
            mascotas='si' if random.random() > 0.5 else 'no',
            descripcion=fake.paragraph(),
            localidad=localidad,
            zona=zona,
            barrio=barrio,
            edificio=edificio,
            cercanias=cercanias,
            estado=random.choice(['pendiente', 'en_proceso', 'completado']),
            edificacion=edificacion,
            prioridad=random.choice(['normal', 'alta', 'baja']),
            fecha_ideal_entrega=fake.future_date(),
            informacion_legal_financiera=info_legal,
            honorarios=honorarios,
            negocibles="Precio, fecha de entrega",
            no_negocibles="Ubicación, número de habitaciones",
            comentarios=comentarios
        )
        
        print(f"Requerimiento creado para {cliente.nombre} {cliente.apellidos}")
        return requerimiento
    except Exception as e:
        print(f"Error al crear requerimiento para {cliente.nombre}: {str(e)}")
        return None

def create_tarea(agente, cliente, propiedad=None, tipo_tarea=None, prioridad=None, estado=None, 
                fecha_vencimiento=None, descripcion=None):
    """Crear una tarea de seguimiento"""
    try:
        # Valores por defecto si no se proporcionan
        if not tipo_tarea:
            tipo_tarea = random.choice([
                'llamada_seguimiento', 'visita_inmueble', 'documentacion', 
                'verificacion_datos', 'cierre'
            ])
        
        if not prioridad:
            prioridad = random.choice(['baja', 'media', 'alta'])
        
        if not estado:
            estado = random.choice(['pendiente', 'en_proceso', 'completada', 'cancelada'])
        
        if not fecha_vencimiento:
            fecha_vencimiento = fake.future_date()
        
        if not descripcion:
            descripciones = {
                'llamada_seguimiento': f"Llamar a {cliente.nombre} para seguimiento",
                'visita_inmueble': f"Visitar inmueble con {cliente.nombre}",
                'documentacion': f"Recopilar documentación de {cliente.nombre}",
                'verificacion_datos': f"Verificar datos de {cliente.nombre}",
                'cierre': f"Cerrar negocio con {cliente.nombre}"
            }
            descripcion = descripciones.get(tipo_tarea, f"Tarea para {cliente.nombre}")
        
        # Crear tarea
        tarea = TareaModel.objects.create(
            fecha_vencimiento=fecha_vencimiento,
            tipo_tarea=tipo_tarea,
            prioridad=prioridad,
            estado=estado,
            descripcion=descripcion,
            agente=agente,
            cliente=cliente,
            propiedad=propiedad
        )
        
        print(f"Tarea creada: {tipo_tarea} para {cliente.nombre}")
        return tarea
    except Exception as e:
        print(f"Error al crear tarea para {cliente.nombre}: {str(e)}")
        return None

def generate_test_data():
    """Generar datos de prueba"""
    print("Iniciando generación de datos de prueba...")
    
    # Datos para los agentes
    agentes_data = [
        {
            'username': 'agente1',
            'first_name': 'Carlos',
            'last_name': 'Rodríguez',
            'email': 'carlos.rodriguez@ejemplo.com',
            'password': 'password123',
            'telefono': '601234567',
            'cedula': ''.join([str(random.randint(0, 9)) for _ in range(10)]),
            'role': 'admin'
        },
        {
            'username': 'agente2',
            'first_name': 'Ana',
            'last_name': 'Martínez',
            'email': 'ana.martinez@ejemplo.com',
            'password': 'password123',
            'telefono': '602345678',
            'cedula': ''.join([str(random.randint(0, 9)) for _ in range(10)]),
            'role': 'user'
        },
        {
            'username': 'agente3',
            'first_name': 'Juan',
            'last_name': 'López',
            'email': 'juan.lopez@ejemplo.com',
            'password': 'password123',
            'telefono': '603456789',
            'cedula': ''.join([str(random.randint(0, 9)) for _ in range(10)]),
            'role': 'user'
        }
    ]
    
    # Crear agentes
    agentes = []
    for data in agentes_data:
        user = create_user(
            username=data['username'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            password=data['password'],
            is_staff=(data['role'] == 'admin')
        )
        
        if user:
            agente = create_agente(
                user=user,
                telefono=data['telefono'],
                cedula=data['cedula'],
                role=data['role']
            )
            if agente:
                agentes.append(agente)
    
    # Crear 5 clientes para cada agente
    for agente in agentes:
        for i in range(5):
            nombre = fake.first_name()
            apellidos = fake.last_name() + " " + fake.last_name()
            telefono = "6" + ''.join([str(random.randint(0, 9)) for _ in range(8)])
            correo = f"{nombre.lower()}.{apellidos.split()[0].lower()}@{fake.free_email_domain()}"
            cedula = ''.join([str(random.randint(0, 9)) for _ in range(10)])
            
            create_cliente(
                agente=agente,
                nombre=nombre,
                apellidos=apellidos,
                telefono=telefono,
                correo=correo,
                cedula=cedula
            )
    
    # Crear 10 amenidades
    amenidades_data = [
        {'nombre': 'Piscina', 'categoria': 'Recreación'},
        {'nombre': 'Gimnasio', 'categoria': 'Deporte'},
        {'nombre': 'Salón comunal', 'categoria': 'Social'},
        {'nombre': 'Parque infantil', 'categoria': 'Recreación'},
        {'nombre': 'Zona BBQ', 'categoria': 'Social'},
        {'nombre': 'Cancha de tenis', 'categoria': 'Deporte'},
        {'nombre': 'Seguridad 24 horas', 'categoria': 'Seguridad'},
        {'nombre': 'Parqueadero visitantes', 'categoria': 'Servicios'},
        {'nombre': 'Jacuzzi', 'categoria': 'Recreación'},
        {'nombre': 'Sauna', 'categoria': 'Bienestar'}
    ]
    
    amenidades = []
    for data in amenidades_data:
        amenidad = create_amenidad(
            nombre=data['nombre'],
            categoria=data['categoria'],
            descripcion=f"Amenidad de {data['categoria']}: {data['nombre']}"
        )
        if amenidad:
            amenidades.append(amenidad)
    
    # Crear 10 características interiores
    caracteristicas_data = [
        {'caracteristica': 'Pisos de madera', 'categoria': 'Acabados', 'tipo_propiedad': 'apartamento'},
        {'caracteristica': 'Cocina integral', 'categoria': 'Cocina', 'tipo_propiedad': 'apartamento'},
        {'caracteristica': 'Closets empotrados', 'categoria': 'Almacenamiento', 'tipo_propiedad': 'apartamento'},
        {'caracteristica': 'Chimenea', 'categoria': 'Confort', 'tipo_propiedad': 'casa'},
        {'caracteristica': 'Ventanas panorámicas', 'categoria': 'Iluminación', 'tipo_propiedad': 'apartamento'},
        {'caracteristica': 'Calefacción central', 'categoria': 'Confort', 'tipo_propiedad': 'casa'},
        {'caracteristica': 'Techo alto', 'categoria': 'Estructura', 'tipo_propiedad': 'casa'},
        {'caracteristica': 'Baño con jacuzzi', 'categoria': 'Baños', 'tipo_propiedad': 'apartamento'},
        {'caracteristica': 'Vestier', 'categoria': 'Almacenamiento', 'tipo_propiedad': 'casa'},
        {'caracteristica': 'Estudio independiente', 'categoria': 'Espacios', 'tipo_propiedad': 'casa'}
    ]
    
    for data in caracteristicas_data:
        create_caracteristica_interior(
            caracteristica=data['caracteristica'],
            categoria=data['categoria'],
            tipo_propiedad=data['tipo_propiedad'],
            descripcion=f"Característica de {data['categoria']}: {data['caracteristica']}"
        )
    
    # Crear 5 localidades
    localidades_data = [
        {'nombre': 'Chapinero', 'sigla': 'CHP'},
        {'nombre': 'Usaquén', 'sigla': 'USQ'},
        {'nombre': 'Suba', 'sigla': 'SUB'},
        {'nombre': 'Teusaquillo', 'sigla': 'TEU'},
        {'nombre': 'Santa Fe', 'sigla': 'STF'}
    ]
    
    localidades = []
    for data in localidades_data:
        localidad = create_localidad(
            nombre=data['nombre'],
            sigla=data['sigla'],
            descripcion=f"Localidad {data['nombre']} en la ciudad"
        )
        if localidad:
            localidades.append(localidad)
    
    # Crear 5 barrios (uno por cada localidad)
    barrios_data = [
        {'nombre': 'Rosales', 'localidad_index': 0, 'estrato': 6, 'tipo': 'residencial'},
        {'nombre': 'Santa Bárbara', 'localidad_index': 1, 'estrato': 5, 'tipo': 'residencial'},
        {'nombre': 'Niza', 'localidad_index': 2, 'estrato': 4, 'tipo': 'residencial'},
        {'nombre': 'Galerías', 'localidad_index': 3, 'estrato': 4, 'tipo': 'mixta'},
        {'nombre': 'La Macarena', 'localidad_index': 4, 'estrato': 3, 'tipo': 'mixta'}
    ]
    
    barrios = []
    for data in barrios_data:
        if len(localidades) > data['localidad_index']:
            barrio = create_barrio(
                nombre=data['nombre'],
                localidad=localidades[data['localidad_index']],
                sigla=data['nombre'][:3].upper(),
                estrato_predominante=data['estrato'],
                tipo_barrio=data['tipo'],
                descripcion=f"Barrio {data['nombre']} en la localidad de {localidades[data['localidad_index']].nombre}"
            )
            if barrio:
                barrios.append(barrio)
    
    # Crear 5 zonas
    zonas_data = [
        {'nombre': 'Zona Norte', 'sigla': 'ZNO', 'tipo': 'residencial'},
        {'nombre': 'Zona Centro', 'sigla': 'ZCE', 'tipo': 'comercial'},
        {'nombre': 'Zona Sur', 'sigla': 'ZSU', 'tipo': 'residencial'},
        {'nombre': 'Zona Occidental', 'sigla': 'ZOC', 'tipo': 'mixta'},
        {'nombre': 'Zona Oriental', 'sigla': 'ZOR', 'tipo': 'industrial'}
    ]
    
    zonas = []
    for data in zonas_data:
        zona = create_zona(
            nombre=data['nombre'],
            sigla=data['sigla'],
            tipo_zona=data['tipo'],
            descripcion=f"Zona {data['nombre']} de tipo {data['tipo']}"
        )
        if zona:
            zonas.append(zona)
            
    # Asignar barrios a zonas
    if len(zonas) >= 3 and len(barrios) >= 5:
        # Zona Norte tiene Rosales y Santa Bárbara
        zonas[0].barrios.add(barrios[0], barrios[1])
        # Zona Centro tiene Galerías
        zonas[1].barrios.add(barrios[3])
        # Zona Sur tiene La Macarena
        zonas[2].barrios.add(barrios[4])
        # Zona Occidental tiene Niza
        zonas[3].barrios.add(barrios[2])
    
    # Crear 10 puntos de interés
    puntos_interes_data = [
        {'nombre': 'Centro Comercial Andino', 'categoria': 'Comercio'},
        {'nombre': 'Parque Simón Bolívar', 'categoria': 'Recreación'},
        {'nombre': 'Universidad Nacional', 'categoria': 'Educación'},
        {'nombre': 'Hospital Santa Fe', 'categoria': 'Salud'},
        {'nombre': 'Estadio El Campín', 'categoria': 'Deporte'},
        {'nombre': 'Museo Nacional', 'categoria': 'Cultura'},
        {'nombre': 'Aeropuerto El Dorado', 'categoria': 'Transporte'},
        {'nombre': 'Biblioteca Virgilio Barco', 'categoria': 'Educación'},
        {'nombre': 'Plaza de Mercado Paloquemao', 'categoria': 'Comercio'},
        {'nombre': 'Catedral Primada', 'categoria': 'Religión'}
    ]
    
    puntos_interes = []
    for data in puntos_interes_data:
        punto = create_punto_de_interes(
            nombre=data['nombre'],
            categoria=data['categoria'],
            descripcion=f"Punto de interés de categoría {data['categoria']}: {data['nombre']}"
        )
        if punto:
            puntos_interes.append(punto)
    
    # Crear 10 zonas de interés
    zonas_interes_data = [
        {'nombre': 'Zona G', 'categoria': 'Gastronomía'},
        {'nombre': 'Zona T', 'categoria': 'Entretenimiento'},
        {'nombre': 'Zona Rosa', 'categoria': 'Comercio'},
        {'nombre': 'Centro Histórico', 'categoria': 'Cultura'},
        {'nombre': 'Zona Industrial', 'categoria': 'Industria'},
        {'nombre': 'Zona Financiera', 'categoria': 'Negocios'},
        {'nombre': 'Corredor Ecológico', 'categoria': 'Ambiental'},
        {'nombre': 'Distrito Tecnológico', 'categoria': 'Tecnología'},
        {'nombre': 'Corredor Universitario', 'categoria': 'Educación'},
        {'nombre': 'Zona Artesanal', 'categoria': 'Cultura'}
    ]
    
    zonas_interes = []
    for data in zonas_interes_data:
        zona_interes = create_zona_de_interes(
            nombre=data['nombre'],
            categoria=data['categoria'],
            descripcion=f"Zona de interés de categoría {data['categoria']}: {data['nombre']}"
        )
        if zona_interes:
            zonas_interes.append(zona_interes)
    
    # Asignar puntos de interés a zonas de interés
    if len(zonas_interes) >= 5 and len(puntos_interes) >= 5:
        # Zona G tiene Centro Comercial Andino
        zonas_interes[0].puntos_de_interes.add(puntos_interes[0])
        # Zona T tiene Estadio El Campín
        zonas_interes[1].puntos_de_interes.add(puntos_interes[4])
        # Zona Rosa tiene Plaza de Mercado Paloquemao
        zonas_interes[2].puntos_de_interes.add(puntos_interes[8])
        # Centro Histórico tiene Museo Nacional y Catedral Primada
        zonas_interes[3].puntos_de_interes.add(puntos_interes[5], puntos_interes[9])
        # Corredor Universitario tiene Universidad Nacional y Biblioteca Virgilio Barco
        zonas_interes[8].puntos_de_interes.add(puntos_interes[2], puntos_interes[7])
    
    # Crear contactos administradores para edificios
    contactos_admin = []
    for i in range(5):
        nombre = fake.name()
        telefono = "6" + ''.join([str(random.randint(0, 9)) for _ in range(8)])
        correo = f"admin{i+1}@edificios.com"
        
        contacto = create_contacto_administrador(
            nombre=nombre,
            telefono=telefono,
            correo=correo
        )
        if contacto:
            contactos_admin.append(contacto)
    
    # Crear 5 edificios
    edificios_data = [
        {'nombre': 'Torres del Parque', 'barrio_index': 0, 'tipo': 'Edificio Residencial', 'torres': 3, 'parqueaderos': 50},
        {'nombre': 'Edificio Santa María', 'barrio_index': 1, 'tipo': 'Edificio Residencial', 'torres': 1, 'parqueaderos': 30},
        {'nombre': 'Conjunto Niza Real', 'barrio_index': 2, 'tipo': 'Conjunto Residencial', 'torres': 5, 'parqueaderos': 100},
        {'nombre': 'Centro Empresarial Galerías', 'barrio_index': 3, 'tipo': 'Edificio Comercial', 'torres': 2, 'parqueaderos': 80},
        {'nombre': 'Residencias La Macarena', 'barrio_index': 4, 'tipo': 'Edificio Residencial', 'torres': 1, 'parqueaderos': 20}
    ]
    
    edificios = []
    for i, data in enumerate(edificios_data):
        if len(barrios) > data['barrio_index'] and len(contactos_admin) > i:
            edificio = create_edificio(
                nombre=data['nombre'],
                barrio=barrios[data['barrio_index']],
                contacto_administrador=contactos_admin[i],
                tipo_edificio=data['tipo'],
                torres=data['torres'],
                parqueaderos=data['parqueaderos']
            )
            if edificio:
                edificios.append(edificio)
    
    # Asignar amenidades a edificios
    if len(edificios) >= 5 and len(amenidades) >= 5:
        # Torres del Parque tiene Piscina, Gimnasio, Salón comunal
        edificios[0].amenidades.add(amenidades[0], amenidades[1], amenidades[2])
        # Edificio Santa María tiene Seguridad 24 horas, Parqueadero visitantes
        edificios[1].amenidades.add(amenidades[6], amenidades[7])
        # Conjunto Niza Real tiene Piscina, Gimnasio, Parque infantil, Zona BBQ, Cancha de tenis
        edificios[2].amenidades.add(amenidades[0], amenidades[1], amenidades[3], amenidades[4], amenidades[5])
        # Centro Empresarial Galerías tiene Seguridad 24 horas, Parqueadero visitantes
        edificios[3].amenidades.add(amenidades[6], amenidades[7])
        # Residencias La Macarena tiene Salón comunal, Parqueadero visitantes
        edificios[4].amenidades.add(amenidades[2], amenidades[7])
    
    # Asignar puntos de interés a edificios
    if len(edificios) >= 5 and len(puntos_interes) >= 5:
        edificios[0].puntos_de_interes = puntos_interes[0]  # Centro Comercial Andino
        edificios[1].puntos_de_interes = puntos_interes[3]  # Hospital Santa Fe
        edificios[2].puntos_de_interes = puntos_interes[1]  # Parque Simón Bolívar
        edificios[3].puntos_de_interes = puntos_interes[2]  # Universidad Nacional
        edificios[4].puntos_de_interes = puntos_interes[5]  # Museo Nacional
    
    # Asignar zonas de interés a edificios
    if len(edificios) >= 5 and len(zonas_interes) >= 5:
        edificios[0].zonas_de_interes = zonas_interes[0]  # Zona G
        edificios[1].zonas_de_interes = zonas_interes[1]  # Zona T
        edificios[2].zonas_de_interes = zonas_interes[6]  # Corredor Ecológico
        edificios[3].zonas_de_interes = zonas_interes[5]  # Zona Financiera
        edificios[4].zonas_de_interes = zonas_interes[3]  # Centro Histórico

    # Crear 15 propiedades
    propiedades = []
    tipos_propiedad = ['apartamento', 'casa', 'lote', 'oficina', 'local']
    
    # Distribuir propiedades entre agentes y edificios/barrios
    if agentes:  # Verificar que haya agentes disponibles
        for i in range(15):
            agente = random.choice(agentes)
            # Seleccionar un cliente aleatorio como propietario
            propietario = ClienteModel.objects.order_by('?').first()
            
            if not propietario:  # Si no hay propietarios, saltar esta iteración
                print("No hay clientes disponibles para asignar como propietarios.")
                continue
            
            tipo_propiedad = random.choice(tipos_propiedad)
            titulo = f"{tipo_propiedad.capitalize()} en {random.choice(['venta', 'arriendo'])}"
            
            # Decidir si la propiedad está en un edificio o solo en un barrio
            if random.random() > 0.5 and edificios:
                edificio = random.choice(edificios)
                barrio = edificio.barrio
                estrato = edificio.estrato
            else:
                edificio = None
                barrio = random.choice(barrios) if barrios else None
                estrato = barrio.estrato_predominante if barrio else random.randint(1, 6)
            
            # Generar características según el tipo de propiedad
            if tipo_propiedad == 'apartamento':
                habitaciones = random.randint(1, 4)
                banos = random.randint(1, 3)
                metro_cuadrado = random.randint(40, 200)
                valor_admin = random.randint(200000, 800000)
            elif tipo_propiedad == 'casa':
                habitaciones = random.randint(2, 6)
                banos = random.randint(2, 4)
                metro_cuadrado = random.randint(80, 400)
                valor_admin = random.randint(0, 500000)
            elif tipo_propiedad == 'lote':
                habitaciones = 0
                banos = 0
                metro_cuadrado = random.randint(200, 2000)
                valor_admin = 0
            else:  # oficina o local
                habitaciones = random.randint(0, 2)
                banos = random.randint(1, 2)
                metro_cuadrado = random.randint(30, 150)
                valor_admin = random.randint(300000, 1000000)
            
            # Seleccionar algunas amenidades aleatorias si hay disponibles
            amenidades_seleccionadas = random.sample(amenidades, min(random.randint(0, 5), len(amenidades))) if amenidades else None
            
            propiedad = create_propiedad(
                agente=agente,
                propietario=propietario,
                titulo=titulo,
                tipo_propiedad=tipo_propiedad,
                edificio=edificio,
                barrio=barrio,
                habitaciones=habitaciones,
                banos=banos,
                metro_cuadrado_construido=metro_cuadrado,
                estrato=estrato,
                valor_administracion=valor_admin,
                amenidades=amenidades_seleccionadas
            )
            
            if propiedad:
                propiedades.append(propiedad)
    else:
        print("No hay agentes disponibles para crear propiedades.")
    
    # Crear 10 requerimientos
    requerimientos = []
    if agentes and ClienteModel.objects.exists():  # Verificar que haya agentes y clientes disponibles
        for i in range(10):
            agente = random.choice(agentes)
            cliente = ClienteModel.objects.order_by('?').first()
            
            # Determinar tipo de negocio
            tipo_negocio = random.choice(["venta", "arriendo", "venta,arriendo"])
            
            # Determinar presupuesto según tipo de negocio
            if "venta" in tipo_negocio:
                presupuesto_min = random.randint(100000000, 300000000)
                presupuesto_max = presupuesto_min + random.randint(50000000, 200000000)
            else:
                presupuesto_min = random.randint(1000000, 3000000)
                presupuesto_max = presupuesto_min + random.randint(500000, 2000000)
            
            # Características deseadas
            habitaciones = random.randint(1, 5)
            banos = random.randint(1, 4)
            area_minima = random.randint(40, 100)
            area_maxima = area_minima + random.randint(20, 100)
            
            # Ubicación deseada
            localidad = random.choice(localidades) if localidades else None
            barrio = random.choice(barrios) if barrios else None
            zona = random.choice(zonas) if zonas else None
            edificio = random.choice(edificios) if random.random() > 0.7 and edificios else None
            
            requerimiento = create_requerimiento(
                agente=agente,
                cliente=cliente,
                tipo_negocio=tipo_negocio,
                presupuesto_min=presupuesto_min,
                presupuesto_max=presupuesto_max,
                habitaciones=habitaciones,
                banos=banos,
                area_minima=area_minima,
                area_maxima=area_maxima,
                localidad=localidad,
                barrio=barrio,
                zona=zona,
                edificio=edificio
            )
            
            if requerimiento:
                requerimientos.append(requerimiento)
    else:
        print("No hay agentes o clientes disponibles para crear requerimientos.")
    
    # Crear 15 tareas
    tareas = []
    if agentes and ClienteModel.objects.exists():  # Verificar que haya agentes y clientes disponibles
        for i in range(15):
            agente = random.choice(agentes)
            cliente = ClienteModel.objects.order_by('?').first()
            
            # Decidir si la tarea está relacionada con una propiedad
            propiedad = random.choice(propiedades) if random.random() > 0.3 and propiedades else None
            
            # Determinar tipo de tarea según si hay propiedad asociada
            if propiedad:
                tipo_tarea = random.choice(['visita_inmueble', 'documentacion', 'cierre'])
            else:
                tipo_tarea = random.choice(['llamada_seguimiento', 'verificacion_datos'])
            
            # Determinar prioridad según el tipo de tarea
            if tipo_tarea in ['cierre', 'visita_inmueble']:
                prioridad = 'alta'
            elif tipo_tarea == 'documentacion':
                prioridad = 'media'
            else:
                prioridad = random.choice(['baja', 'media'])
            
            # Determinar estado
            estado = random.choice(['pendiente', 'en_proceso', 'completada', 'cancelada'])
            
            # Determinar fecha de vencimiento
            if estado in ['pendiente', 'en_proceso']:
                fecha_vencimiento = fake.future_date()
            else:
                fecha_vencimiento = fake.past_date()
            
            # Crear descripción personalizada
            if propiedad:
                descripcion = f"{tipo_tarea.replace('_', ' ').title()} para {cliente.nombre} {cliente.apellidos} relacionada con {propiedad.titulo}"
            else:
                descripcion = f"{tipo_tarea.replace('_', ' ').title()} para {cliente.nombre} {cliente.apellidos}"
            
            tarea = create_tarea(
                agente=agente,
                cliente=cliente,
                propiedad=propiedad,
                tipo_tarea=tipo_tarea,
                prioridad=prioridad,
                estado=estado,
                fecha_vencimiento=fecha_vencimiento,
                descripcion=descripcion
            )
            
            if tarea:
                tareas.append(tarea)
    else:
        print("No hay agentes o clientes disponibles para crear tareas.")

if __name__ == "__main__":
    # Verificar si ya existen datos para evitar duplicados
    if User.objects.filter(username='agente1').exists() or AgenteModel.objects.exists():
        print("Los datos de prueba ya existen. Eliminando datos existentes...")
        
        # Eliminar todos los clientes primero (para evitar problemas de integridad referencial)
        print("Eliminando clientes...")
        ClienteModel.objects.all().delete()
        
        # Eliminar propiedades, requerimientos y tareas
        print("Eliminando propiedades, requerimientos y tareas...")
        PropiedadModel.objects.all().delete()
        RequerimientoModel.objects.all().delete()
        TareaModel.objects.all().delete()
        
        # Eliminar todos los agentes
        print("Eliminando agentes...")
        AgenteModel.objects.all().delete()
        
        # Eliminar usuarios específicos
        print("Eliminando usuarios...")
        User.objects.filter(username__in=['agente1', 'agente2', 'agente3']).delete()
        
        # Eliminar otros modelos
        print("Eliminando otros modelos...")
        EdificioModel.objects.all().delete()
        ContactoAdministradorModel.objects.all().delete()
        ZonasDeInteresModel.objects.all().delete()
        PuntoDeInteresModel.objects.all().delete()
        ZonaModel.objects.all().delete()
        BarrioModel.objects.all().delete()
        LocalidadModel.objects.all().delete()
        CaracteristicasInterioresModel.objects.all().delete()
        AmenidadesModel.objects.all().delete()
        
        print("Datos eliminados. Generando nuevos datos...")
    
    generate_test_data()
    print("Generación de datos de prueba completada.")
