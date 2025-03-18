from asgiref.sync import sync_to_async
from crm.models import EdificioModel, PropiedadModel, LocalidadModel

class DataFetcher:
    @staticmethod
    @sync_to_async
    def get_edificio_data(edificio_id):
        edificio = EdificioModel.objects.get(id=edificio_id)
        return {
            'nombre': edificio.nombre,
            'direccion': edificio.direccion,
            'descripcion': edificio.descripcion,
            'estado': edificio.estado,
            'tipo_edificio': edificio.tipo_edificio,
            'estrato': edificio.estrato,
            'unidades': edificio.unidades,
            'torres': edificio.torres,
            'parqueaderos': edificio.parqueaderos,
            'ano_construccion': edificio.ano_construccion,
            'servicios_adicionales': edificio.servicios_adicionales,
        }

    @staticmethod
    @sync_to_async
    def get_propiedad_data(propiedad_id):
        propiedad = PropiedadModel.objects.get(id=propiedad_id)
        return {
            'titulo': propiedad.titulo,
            'tipo_propiedad': propiedad.tipo_propiedad,
            'metro_cuadrado_construido': propiedad.metro_cuadrado_construido,
            'habitaciones': propiedad.habitaciones,
            'banos': propiedad.banos,
            'estrato': propiedad.estrato,
            'valor_administracion': propiedad.valor_administracion,
            'descripcion': propiedad.descripcion,
            'direccion': propiedad.direccion,
            'ano_construccion': propiedad.ano_construccion,
            'garajes': propiedad.garajes,
            'depositos': propiedad.depositos,
            'mascotas': propiedad.mascotas,
            'nivel': propiedad.nivel,
            'terrazas': propiedad.terraza,
            'balcon': propiedad.balcon,
            # Agregar más campos según sea necesario
        }

    @staticmethod
    @sync_to_async
    def get_localidad_data(localidad_id):
        try:
            localidad = LocalidadModel.objects.get(id=localidad_id)
        except LocalidadModel.DoesNotExist:
            return None  # O manejar el error de otra manera según tu lógica

        zonas_de_interes = localidad.zonas_de_interes
        return {
            'nombre': localidad.nombre,
            'descripcion': localidad.descripcion,
            'zonas_de_interes': list(zonas_de_interes.all().values_list('nombre', flat=True)) if zonas_de_interes else []
        } 