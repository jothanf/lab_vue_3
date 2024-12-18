from rest_framework import serializers
from .models import AmenidadesModel, CaracteristicasInterioresModel, ZonasDeInteresModel, LocalidadModel, BarrioModel, ZonaModel, EdificioModel, PropiedadModel, AgenteModel, ClienteModel, MultimediaModel, RequerimientoModel, TareaModel, FaseSeguimientoModel
import json

class MultimediaModelSerializer(serializers.ModelSerializer):
    archivo_url = serializers.SerializerMethodField()

    class Meta:
        model = MultimediaModel
        fields = ['id', 'tipo', 'archivo', 'titulo', 'descripcion', 'es_principal', 'archivo_url']

    def get_archivo_url(self, obj):
        if obj.archivo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.archivo.url)
            return obj.archivo.url
        return None

class AmenidadesModelSerializer(serializers.ModelSerializer):
    icono_url = serializers.SerializerMethodField()

    class Meta:
        model = AmenidadesModel
        fields = ['id', 'nombre', 'categoria', 'descripcion', 'icono', 'icono_url']

    def get_icono_url(self, obj):
        if obj.icono:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.icono.url)
        return None

class CaracteristicasInterioresModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaracteristicasInterioresModel
        fields = '__all__'  

class ZonasDeInteresModelSerializer(serializers.ModelSerializer):
    multimedia = MultimediaModelSerializer(many=True, read_only=True)
    icono_url = serializers.SerializerMethodField()

    class Meta:
        model = ZonasDeInteresModel
        fields = ['id', 'nombre', 'categoria', 'descripcion', 'ubicacion', 'multimedia', 'icono', 'icono_url', 'direccion']

    def get_icono_url(self, obj):
        if obj.icono:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.icono.url)
            return obj.icono.url
        return None

class LocalidadModelSerializer(serializers.ModelSerializer):
    multimedia = MultimediaModelSerializer(many=True, read_only=True)
    zonas_de_interes = ZonasDeInteresModelSerializer(many=True, read_only=True)

    class Meta:
        model = LocalidadModel
        fields = ['id', 'nombre', 'sigla', 'descripcion', 'multimedia', 'zonas_de_interes']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # Obtener multimedia de la localidad
        multimedia = MultimediaModel.objects.filter(
            content_type__model='localidadmodel',
            object_id=instance.id
        )
        
        representation['multimedia'] = MultimediaModelSerializer(
            multimedia, 
            many=True,
            context=self.context
        ).data

        # Asegurarse de que las zonas de interés se serialicen correctamente
        if hasattr(instance, 'zonas_de_interes'):
            representation['zonas_de_interes'] = ZonasDeInteresModelSerializer(
                instance.zonas_de_interes.all(),
                many=True,
                context=self.context
            ).data
        
        return representation

    def update(self, instance, validated_data):
        # Obtener las zonas de interés del request data
        zonas_ids = self.context['request'].data.get('zonas_de_interes', [])
        
        # Actualizar los campos básicos
        instance = super().update(instance, validated_data)
        
        # Actualizar las zonas de interés
        if zonas_ids:
            # Convertir a lista si es string
            if isinstance(zonas_ids, str):
                zonas_ids = json.loads(zonas_ids)
            # Limpiar y establecer nuevas zonas
            instance.zonas_de_interes.clear()
            instance.zonas_de_interes.add(*zonas_ids)
        
        return instance

class BarrioModelSerializer(serializers.ModelSerializer):
    multimedia = MultimediaModelSerializer(many=True, read_only=True)
    localidad_nombre = serializers.CharField(source='localidad.nombre', read_only=True)
    localidad = serializers.PrimaryKeyRelatedField(
        queryset=LocalidadModel.objects.all(),
        required=True
    )
    zonas_de_interes = ZonasDeInteresModelSerializer(many=True, read_only=True)
    zonas_de_interes_ids = serializers.PrimaryKeyRelatedField(
        source='zonas_de_interes',
        queryset=ZonasDeInteresModel.objects.all(),
        many=True,
        required=False,
        write_only=True
    )

    class Meta:
        model = BarrioModel
        fields = [
            'id', 'nombre', 'sigla', 'descripcion', 
            'localidad', 'localidad_nombre',
            'estrato_predominante', 'tipo_barrio', 
            'multimedia', 'zonas_de_interes', 'zonas_de_interes_ids'
        ]

    def update(self, instance, validated_data):
        # Manejar la localidad
        localidad_data = validated_data.pop('localidad', None)
        if localidad_data:
            instance.localidad = localidad_data

        # Manejar zonas de interés si están presentes
        if 'zonas_de_interes' in validated_data:
            instance.zonas_de_interes.set(validated_data.pop('zonas_de_interes'))

        # Actualizar los demás campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # Asegurarse de que localidad sea el ID en la respuesta
        if isinstance(representation.get('localidad'), dict):
            representation['localidad'] = representation['localidad']['id']
            
        return representation

class ZonaModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZonaModel
        fields = '__all__'  

class EdificioModelSerializer(serializers.ModelSerializer):
    multimedia = MultimediaModelSerializer(many=True, read_only=True)
    zonas_de_interes = ZonasDeInteresModelSerializer(many=True, read_only=True)
    zonas_de_interes_ids = serializers.PrimaryKeyRelatedField(
        source='zonas_de_interes',
        queryset=ZonasDeInteresModel.objects.all(),
        many=True,
        required=False,
        write_only=True
    )
    barrio_nombre = serializers.CharField(source='barrio.nombre', read_only=True)
    amenidades = AmenidadesModelSerializer(many=True, read_only=True)
    amenidades_ids = serializers.PrimaryKeyRelatedField(
        source='amenidades',
        queryset=AmenidadesModel.objects.all(),
        many=True,
        required=False,
        write_only=True
    )

    class Meta:
        model = EdificioModel
        fields = [
            'id', 'nombre', 'sigla', 'desarrollador', 
            'descripcion', 'direccion', 'estrato', 
            'telefono', 'barrio', 'barrio_nombre',
            'multimedia', 'zonas_de_interes', 'zonas_de_interes_ids',
            'amenidades', 'amenidades_ids', 'tipo_edificio', 'estado'
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # Obtener multimedia del edificio
        multimedia = MultimediaModel.objects.filter(
            content_type__model='edificiomodel',
            object_id=instance.id
        )
        
        representation['multimedia'] = MultimediaModelSerializer(
            multimedia, 
            many=True,
            context=self.context
        ).data
        
        return representation

    def update(self, instance, validated_data):
        print("Datos validados en update:", validated_data)
        
        # Manejar amenidades si están presentes
        if 'amenidades' in validated_data:
            instance.amenidades.set(validated_data.pop('amenidades'))
        
        # Manejar zonas de interés si están presentes
        if 'zonas_de_interes' in validated_data:
            instance.zonas_de_interes.set(validated_data.pop('zonas_de_interes'))
        
        # Actualizar los demás campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class PropiedadModelSerializer(serializers.ModelSerializer):
    amenidades = AmenidadesModelSerializer(many=True, read_only=True)
    multimedia = MultimediaModelSerializer(many=True, read_only=True)
    
    class Meta:
        model = PropiedadModel
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        if instance.amenidades.exists():
            representation['amenidades'] = AmenidadesModelSerializer(
                instance.amenidades.all(), 
                many=True
            ).data
       
        multimedia = MultimediaModel.objects.filter(
            content_type__model='propiedadmodel',
            object_id=instance.id
        )
        representation['multimedia'] = MultimediaModelSerializer(multimedia, many=True).data
        print("Multimedia encontrada:", representation['multimedia'])
        return representation

    def validate(self, data):
        print("\n=== Validación del Serializador ===")
        print("Datos entrantes completos:", self.initial_data)
        
        propietario_id = self.initial_data.get('propietario')
        if not propietario_id:
            raise serializers.ValidationError({
                'propietario': "El campo 'propietario' es requerido"
            })
        
        try:
            propietario = ClienteModel.objects.get(id=propietario_id)
            data['propietario'] = propietario
        except ClienteModel.DoesNotExist:
            raise serializers.ValidationError({
                'propietario': f"No existe un propietario con el ID {propietario_id}"
            })

        agente_id = self.initial_data.get('agente')
        if agente_id:
            try:
                agente = AgenteModel.objects.get(id=agente_id)
                data['agente'] = agente
            except AgenteModel.DoesNotExist:
                raise serializers.ValidationError({
                    'agente': f"No existe un agente con el ID {agente_id}"
                })
            
        edificio_id = self.initial_data.get('edificio')
        if edificio_id:
            try:
                edificio = EdificioModel.objects.get(id=edificio_id)
                data['edificio'] = edificio
            except EdificioModel.DoesNotExist:
                raise serializers.ValidationError({
                    'edificio': f"No existe un edificio con el ID {edificio_id}"
                })

        print("Datos finales validados:", data)
        return data

    def create(self, validated_data):
        print("\n=== Creación de Propiedad ===")
        print("Datos validados para crear:", validated_data)
        try:
            propiedad = PropiedadModel.objects.create(**validated_data)
            print(f"Propiedad creada exitosamente: {propiedad}")
            return propiedad
        except Exception as e:
            print(f"Error al crear propiedad: {str(e)}")
            raise serializers.ValidationError(f"Error al crear la propiedad: {str(e)}")

class RequerimientoModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequerimientoModel
        fields = '__all__'  

class TareaModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareaModel
        fields = '__all__'  

class FaseSeguimientoModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaseSeguimientoModel
        fields = '__all__'
