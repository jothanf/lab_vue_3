from django.db import models
from accounts.models import AgenteModel, ClienteModel
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

class AmenidadesModel(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    icono = models.ImageField(upload_to='iconos/amenidades/', blank=True, null=True)

class CaracteristicasInterioresModel(models.Model):
    caracteristica = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)
    tipo_propiedad = models.CharField(max_length=100, blank=True, null=True, help_text="""
        apartamento, casa, lote
    """)
    descripcion = models.TextField(blank=True, null=True)
    icono = models.ImageField(upload_to='iconos/caracteristicas/', blank=True, null=True)

class ZonasDeInteresModel(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    ubicacion = models.JSONField(null=True, blank=True)
    icono = models.ImageField(upload_to='iconos/zonas/', blank=True, null=True)
    multimedia = GenericRelation('MultimediaModel', related_query_name='zona_de_interes')
    puntos_de_interes = models.ManyToManyField('PuntoDeInteresModel', blank=True)

    def __str__(self):
        return self.nombre
    
class PuntoDeInteresModel(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    ubicacion = models.JSONField(null=True, blank=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    multimedia = GenericRelation('MultimediaModel', related_query_name='punto_de_interes')
    icono = models.ImageField(upload_to='iconos/zonas/', blank=True, null=True)

    def __str__(self):
        return self.nombre

class EdificacionModel(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

class PropiedadModel(models.Model):
    agente = models.ForeignKey(
        AgenteModel, 
        on_delete=models.CASCADE,
        blank=True,  
        null=True 
    )
    propietario = models.ForeignKey(ClienteModel, on_delete=models.CASCADE, blank=True, null=True   )
    titulo = models.CharField(max_length=100, blank=True, null=True)
    modalidad_de_negocio = models.JSONField(null=True, blank=True)
    tipo_propiedad = models.CharField(max_length=100, null=True, blank=True)
    edificio = models.ForeignKey('EdificioModel', on_delete=models.SET_NULL, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    direccion = models.JSONField(blank=True, null=True, help_text="""
        Formato esperado:
        {
            "direccion": "Calle 123",
            "datos_adicionales": {
                "interior": "123",
                "torre": "A",
                "apartamento": "101"
            },
            "coordenada_1": "1234567890",
            "coordenada_2": "0987654321"
        }
        """
    )
    nivel = models.IntegerField(null=True, blank=True)
    metro_cuadrado_construido = models.IntegerField(null=True, blank=True)
    metro_cuadrado_propiedad = models.IntegerField(null=True, blank=True)
    habitaciones = models.IntegerField(default=0, null=True, blank=True)
    habitacion_de_servicio = models.IntegerField(default=0, null=True, blank=True)
    banos = models.IntegerField(default=0, null=True, blank=True)
    terraza = models.CharField(max_length=50, default='no', null=True, blank=True, help_text="""
        una terraza de 10 m2
    """)
    balcon = models.CharField (max_length=50, default='no', null=True, blank=True, help_text="""
        un balcón de 10 m2
    """)
    garajes = models.JSONField(null=True, blank=True, help_text="""
        Formato esperado:
        {
            "cantidad": "1",
            "id": "1234567890"
        }
    """)
    depositos = models.JSONField(null=True, blank=True, help_text="""
        Formato esperado:
        {
            "cantidad": "1",
            "id": "1234567890"
        }
    """)
    mascotas = models.CharField(max_length=2, default='no', blank=True, null=True, choices=[
        ('si', 'Sí'),
        ('no', 'No'),
    ])
    estrato = models.IntegerField(null=True, blank=True)
    valor_predial = models.IntegerField(default=0, null=True, blank=True)
    valor_administracion = models.IntegerField(default=0, null=True, blank=True)
    ano_construccion = models.IntegerField(null=True, blank=True)
    caracteristicas_interiores = models.ForeignKey ('CaracteristicasInterioresModel', on_delete=models.SET_NULL, blank=True, null=True)
    amenidades = models.ManyToManyField('AmenidadesModel', blank=True)
    puntos_de_interes = models.ForeignKey('PuntoDeInteresModel', on_delete=models.SET_NULL, blank=True, null=True)
    zonas_de_interes = models.ForeignKey('ZonasDeInteresModel', on_delete=models.SET_NULL, blank=True, null=True)
    #informacion_legal_financiera = models.JSONField(blank=True, null=True, help_text="""
    #    Formato esperado:
    #    {
    #        "certificado libertat y tadicion": "si",
    #        "hipoteca":"si"
    #    }
    #""")
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    codigo = models.CharField(max_length=50, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    notas = models.JSONField(blank=True, null=True) 
    honorarios = models.JSONField(blank=True, null=True)
    multimedia = GenericRelation('MultimediaModel', related_query_name='propiedad', blank=True, null=True)

    """
    def generar_codigo(self):

        try:
            # Obtener siglas con valor por defecto 'NN'
            localidad_sigla = getattr(self.localidad, 'sigla', 'NN') if self.localidad else 'NN'
            barrio_sigla = getattr(self.barrio, 'sigla', 'NN') if self.barrio else 'NN'
            edificio_sigla = getattr(self.edificio, 'sigla', 'NN') if self.edificio else 'NN'
            zona_sigla = getattr(self.zona, 'sigla', 'NN') if self.zona else 'NN'
            
            # Usar metro_cuadrado_construido como área si está disponible
            area = str(self.metro_cuadrado_construido) if self.metro_cuadrado_construido else 'NN'
            
            codigo = f"{self.id}-{localidad_sigla}-{zona_sigla}-{barrio_sigla}-{edificio_sigla}-{area}"
            return codigo.upper()
        except Exception as e:
            # Si algo falla, retornar un código genérico
            return f"PROP-{self.id}"

    def save(self, *args, **kwargs):
       
        try:
            # Si es un objeto nuevo (sin ID) primero guardamos para obtener el ID
            if not self.id:
                super().save(*args, **kwargs)
                self.codigo = self.generar_codigo()
                return super().save(*args, **kwargs)
            # Si el objeto ya existe y no tiene código, lo generamos
            if not self.codigo:
                self.codigo = self.generar_codigo()
            return super().save(*args, **kwargs)
        except Exception as e:
            # Si algo falla durante el guardado, asegurarse de que tenga un código básico
            if not self.codigo:
                self.codigo = f"PROP-{self.id}" if self.id else "PROP-NEW"
            return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo or 'Sin código'} - {self.nombre or 'Sin nombre'}"
    """

class MultimediaModel(models.Model):
    TIPO_CHOICES = [
        ('foto', 'Fotografía'),
        ('video', 'Video'),
    ]
    
    # Campos para la relación genérica
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    contenido = GenericForeignKey('content_type', 'object_id')
    
    # Campos existentes
    tipo = models.CharField(max_length=5, choices=TIPO_CHOICES)
    archivo = models.FileField(upload_to='multimedia/')
    titulo = models.CharField(max_length=100, blank=True)
    descripcion = models.TextField(blank=True)
    es_principal = models.BooleanField(default=False)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Multimedia'
        verbose_name_plural = 'Multimedia'
        ordering = ['-es_principal', '-fecha_subida']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.titulo}"
    
class RequerimientoModel(models.Model):
    agente = models.ForeignKey(AgenteModel, on_delete=models.CASCADE, null=True, blank=True)
    cliente = models.ForeignKey(ClienteModel, on_delete=models.CASCADE, null=True, blank=True)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    tiempo_estadia = models.IntegerField(blank=True, null=True)
    tipo_negocio = models.JSONField()
    presupuesto_minimo = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    presupuesto_maximo = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    presupuesto_minimo_compra = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    presupuesto_maximo_compra = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    habitantes = models.IntegerField(default=0)
    area_minima = models.IntegerField(null=True, blank=True)
    area_maxima = models.IntegerField(null=True, blank=True)
    area_lote = models.IntegerField(null=True, blank=True)
    habitaciones = models.IntegerField(default=0)
    habitaciones_servicio = models.IntegerField(default=0)
    banos = models.IntegerField(default=0)
    parqueaderos = models.IntegerField(default=0)
    depositos = models.IntegerField(default=0)
    mascotas = models.CharField(max_length=2, default='no', choices=[
        ('si', 'Sí'),
        ('no', 'No'),
    ])
    descripcion = models.TextField(blank=True, null=True)
    localidad = models.ForeignKey('LocalidadModel', on_delete=models.SET_NULL, blank=True, null=True)
    zona = models.ForeignKey('ZonaModel', on_delete=models.SET_NULL, blank=True, null=True)
    barrio = models.ForeignKey('BarrioModel', on_delete=models.SET_NULL, blank=True, null=True)
    edificio = models.ForeignKey('EdificioModel', on_delete=models.SET_NULL, blank=True, null=True)
    cercanias = models.JSONField(blank=True, null=True)
    estado = models.CharField(max_length=20, default='pendiente', choices=[
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado'),
    ])
    edificacion = models.JSONField(
        blank=True, 
        null=True,
        help_text="""
        Formato esperado:
        {
            "tipos": ["centro_comercial", "centro_empresarial", "condominio_campestre", 
                     "edificio_independiente", "independiente", "parcelacion", 
                     "unidad_cerrada", "unidad_cerrada_con_zonas_comunes"]
        }
        """
    )
    prioridad = models.CharField(max_length=20, default='normal', help_text ="""
        normal, alta, baja
    """)
    fecha_ideal_entrega = models.DateTimeField(null=True, blank=True)
    informacion_legal_financiera = models.JSONField(blank=True, null=True)
    honorarios = models.JSONField(blank=True, null=True)
    negocibles = models.TextField(blank=True, null=True)
    no_negocibles = models.TextField(blank=True, null=True)
    comentarios = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = 'requerimientos'
        indexes = [
            models.Index(fields=['tipo_negocio']),
            models.Index(fields=['estado']),
        ]

    def __str__(self):
        return f'Requerimiento de {self.cliente.nombre} - {self.tipo_negocio}'
    
class ContactoAdministradorModel(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField(max_length=100)
    
class EdificioModel(models.Model):
    nombre = models.CharField(max_length=100)
    contacto_administrador = models.ForeignKey('ContactoAdministradorModel', on_delete=models.SET_NULL, blank=True, null=True)
    sigla = models.CharField(max_length=10, blank=True)
    desarrollador = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=50, default='Entregado')
    tipo_edificio = models.CharField(max_length=100, default='Edificio Residencial')
    barrio = models.ForeignKey('BarrioModel', on_delete=models.SET_NULL, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    estrato = models.IntegerField(null=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    unidades = models.JSONField(blank=True, null=True, help_text="""
        {
            "tipos_apartamentos": [
                {
                    "modelo": "Apartamento 3 piezas",
                    "area": 40,
                    "precio": 200000000,
                    "cantidad_disponible": 10
                },
                {
                    "modelo": "Apartamento 3 piezas",
                    "area": 50,
                    "precio": 250000000,
                    "cantidad_disponible": 8
                }
            ]
        }
    """)
    torres = models.IntegerField(default=1)
    parqueaderos = models.IntegerField(default=0)
    descripcion = models.TextField(blank=True, null=True)
    ubicacion = models.JSONField(max_length=255, blank=True, null=True, help_text="""
        {
            "latitud": "1234567890",
            "longitud": "0987654321"
        }
    """ )
    ano_construccion = models.IntegerField(null=True, blank=True)
    servicios_adicionales = models.TextField(blank=True, null=True)
    amenidades = models.ManyToManyField(AmenidadesModel, related_name='edificios', blank=True)
    puntos_de_interes = models.ForeignKey('PuntoDeInteresModel', on_delete=models.SET_NULL, related_name='edificios', blank=True, null=True)
    zonas_de_interes = models.ForeignKey('ZonasDeInteresModel', on_delete=models.SET_NULL, related_name='edificios', blank=True, null=True)
    multimedia = GenericRelation('MultimediaModel', related_query_name='edificio')

    def __str__(self):
        return self.nombre or "Sin nombre"
    

class LocalidadModel(models.Model):
    nombre = models.CharField(max_length=100)
    sigla = models.CharField(max_length=10, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    puntos_de_interes = models.ForeignKey('PuntoDeInteresModel', on_delete=models.SET_NULL, related_name='localidades', blank=True, null=True)
    zonas_de_interes = models.ForeignKey('ZonasDeInteresModel', on_delete=models.SET_NULL, related_name='localidades', blank=True, null=True)
    multimedia = GenericRelation('MultimediaModel')

    def __str__(self):
        return self.nombre
    
class ZonaModel(models.Model):
    nombre = models.CharField(max_length=100)
    sigla = models.CharField(max_length=10, blank=True)
    descripcion = models.TextField(blank=True, null=True)
    tipo_zona = models.CharField(max_length=20)
    barrios = models.ManyToManyField('BarrioModel', related_name='zonas', blank=True)

    def __str__(self):
        return self.nombre or "Sin nombre"

class BarrioModel(models.Model):
    nombre = models.CharField(max_length=100)
    sigla = models.CharField(max_length=10, blank=True)
    descripcion = models.TextField(blank=True, null=True)
    localidad = models.ForeignKey('LocalidadModel', on_delete=models.CASCADE)
    estrato_predominante = models.IntegerField(null=True, blank=True)
    tipo_barrio = models.CharField(max_length=20, choices=[
        ('residencial', 'Residencial'),
        ('comercial', 'Comercial'),
        ('mixta', 'Mixta'),
        ('industrial', 'Industrial'),
    ],
    default='residencial'
    )
    puntos_de_interes = models.ForeignKey('PuntoDeInteresModel', on_delete=models.SET_NULL, related_name='barrios', blank=True, null=True)
    zonas_de_interes = models.ForeignKey('ZonasDeInteresModel', on_delete=models.SET_NULL, related_name='barrios', blank=True, null=True)
    multimedia = GenericRelation('MultimediaModel', related_query_name='barrio')

    def __str__(self):
        return self.nombre or "Sin nombre"

class TareaModel(models.Model):
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_vencimiento = models.DateTimeField()
    tipo_tarea = models.CharField(
        max_length=50,
        choices=[
            ('llamada_seguimiento', 'Llamada de Seguimiento'),
            ('visita_inmueble', 'Visita a Inmueble'),
            ('documentacion', 'Documentación'),
            ('verificacion_datos', 'Verificación de Datos'),
            ('cierre', 'Cierre'),
        ]
    )
    prioridad = models.CharField(
        max_length=20,
        choices=[
            ('baja', 'Baja'),
            ('media', 'Media'),
            ('alta', 'Alta'),
        ]
    )
    estado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('en_proceso', 'En Proceso'),
            ('completada', 'Completada'),
            ('cancelada', 'Cancelada'),
        ]
    )
    descripcion = models.TextField()
    agente = models.ForeignKey(AgenteModel, on_delete=models.CASCADE)
    cliente = models.ForeignKey(ClienteModel, on_delete=models.CASCADE)
    propiedad = models.ForeignKey('PropiedadModel', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.tipo_tarea} - {self.estado}'
    
class FaseSeguimientoModel(models.Model):
    tarea = models.ForeignKey('TareaModel', related_name='fases', on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    descripcion = models.TextField()
    agente_responsable = models.ForeignKey(AgenteModel, on_delete=models.SET_NULL, null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('en_proceso', 'En Proceso'),
            ('completada', 'Completada'),
            ('cancelada', 'Cancelada'),
        ]
    )
    archivos_adjuntos = models.FileField(upload_to='fases_seguimiento/', null=True, blank=True)
    notas_internas = models.TextField(blank=True, null=True)
    resultado = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f'Fase {self.estado} - {self.tarea}'

class AIQueryModel(models.Model):
    QUERY_TYPES = [
        ('description', 'Descripción de propiedad'),
        ('voice', 'Transcripción de voz'),
        ('image', 'Análisis de imagen'),
    ]
    
    MODEL_TYPES = [
        ('gpt-4o-mini', 'GPT-4o-mini'),
        ('gpt-4', 'GPT-4'),
        ('whisper', 'Whisper'),
        ('dalle', 'DALL-E'),
    ]
    
    query_type = models.CharField(max_length=20, choices=QUERY_TYPES)
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES)
    input_data = models.JSONField()
    output_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')
    error_message = models.TextField(null=True, blank=True)


class AgendaModel(models.Model):
    cliente = models.ForeignKey(ClienteModel, on_delete=models.CASCADE)
    agente = models.ForeignKey(AgenteModel, on_delete=models.CASCADE, null=True, blank=True)
    fecha = models.DateField()
    hora = models.TimeField()
    propiedad = models.ForeignKey('PropiedadModel', on_delete=models.CASCADE, null=True, blank=True)
    estado = models.CharField(max_length=20, default='pendiente')
    notas = models.TextField(blank=True, null=True)
