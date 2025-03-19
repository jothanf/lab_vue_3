from django.shortcuts import render, redirect
from rest_framework import viewsets
from .models import AmenidadesModel, CaracteristicasInterioresModel, ZonasDeInteresModel, LocalidadModel, BarrioModel, ZonaModel, EdificioModel, PropiedadModel, MultimediaModel, RequerimientoModel, TareaModel, FaseSeguimientoModel, AIQueryModel, PuntoDeInteresModel, AgendaModel, AgendaAbiertaModel
from .serializers import AmenidadesModelSerializer, CaracteristicasInterioresModelSerializer, ZonasDeInteresModelSerializer, LocalidadModelSerializer, BarrioModelSerializer, ZonaModelSerializer, EdificioModelSerializer, PropiedadModelSerializer, MultimediaModelSerializer, RequerimientoModelSerializer, TareaModelSerializer, FaseSeguimientoModelSerializer, PuntoDeInteresModelSerializer, AgendaModelSerializer, AgendaAbiertaModelSerializer   
from rest_framework.response import Response
from rest_framework import status
import json
from accounts.models import AgenteModel
from django.contrib.contenttypes.models import ContentType
from rest_framework.decorators import action, api_view
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import logging
from .IA.lab_openAI import AIService
import tempfile
import os
import requests
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import sys
from agentesIA.tools.agendaAI import AgenteAgenda

logger = logging.getLogger(__name__)

# Asegúrate de que el directorio del agente está en sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'agentesIA', 'lab'))

# Importar la clase del agente inmobiliario
from requerimiento import AgenteInmobiliario, agente
from propiedad import agente_propiedad

# Create your views here.

class AmenidadesModelViewSet(viewsets.ModelViewSet):
    queryset = AmenidadesModel.objects.all()
    serializer_class = AmenidadesModelSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def list(self, request, *args, **kwargs):
        try:
            logger.info("Iniciando listado de amenidades")
            queryset = self.get_queryset()
            logger.info(f"Cantidad de amenidades: {queryset.count()}")
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error al listar amenidades: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            amenidad = serializer.save()
            print(f"Amenidad creada: {amenidad}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Error al crear amenidad: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CaracteristicasInterioresModelViewSet(viewsets.ModelViewSet):
    queryset = CaracteristicasInterioresModel.objects.all()
    serializer_class = CaracteristicasInterioresModelSerializer

class ZonasDeInteresModelViewSet(viewsets.ModelViewSet):
    queryset = ZonasDeInteresModel.objects.all()
    serializer_class = ZonasDeInteresModelSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error al obtener detalles de zona de interés: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'])
    def agregar_multimedia(self, request, pk=None):
        try:
            zona = self.get_object()
            archivo = request.FILES.get('archivo')
            titulo = request.data.get('titulo', '')
            descripcion = request.data.get('descripcion', '')
            tipo = request.data.get('tipo', 'foto')

            multimedia = MultimediaModel.objects.create(
                content_type=ContentType.objects.get_for_model(zona),
                object_id=zona.id,
                archivo=archivo,
                titulo=titulo,
                descripcion=descripcion,
                tipo=tipo
            )

            serializer = self.get_serializer(zona, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            data = request.data.copy()
            
            # Log para debugging
            print("Datos recibidos:", data)
            
            # Actualizar puntos de interés si se proporcionan
            if 'puntos_de_interes' in data:
                try:
                    puntos_ids = json.loads(data['puntos_de_interes'])
                    print("Puntos de interés IDs:", puntos_ids)  # Log para debugging
                    instance.puntos_de_interes.set(puntos_ids)
                except json.JSONDecodeError as e:
                    print("Error al decodificar JSON:", str(e))  # Log para debugging
                    return Response(
                        {'error': f'Error en formato JSON: {str(e)}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Actualizar otros campos
            serializer = self.get_serializer(instance, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            # Manejar nueva multimedia
            multimedia_files = request.FILES.getlist('multimedia')
            if multimedia_files:
                content_type = ContentType.objects.get_for_model(instance)
                for archivo in multimedia_files:
                    MultimediaModel.objects.create(
                        content_type=content_type,
                        object_id=instance.id,
                        archivo=archivo,
                        tipo='foto'
                    )
            
            return Response(serializer.data)
        except Exception as e:
            print("Error en update:", str(e))  # Log para debugging
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def create(self, request, *args, **kwargs):
        try:
            data = request.data.copy()
            
            # Extraer puntos de interés si existen
            puntos_de_interes = []
            if 'puntos_de_interes' in data:
                puntos_de_interes = json.loads(data.pop('puntos_de_interes'))
            
            # Manejar archivos multimedia
            multimedia_files = request.FILES.getlist('multimedia')
            
            # Crear el serializer con el contexto necesario
            serializer = self.get_serializer(
                data=data,
                context={
                    'request': request,
                    'puntos_de_interes': puntos_de_interes,
                    'multimedia_files': multimedia_files
                }
            )
            
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            data = request.data.copy()
            
            # Actualizar puntos de interés si se proporcionan
            if 'puntos_de_interes' in data:
                try:
                    puntos_ids = json.loads(data['puntos_de_interes'])
                    print("Puntos de interés IDs:", puntos_ids)  # Log para debugging
                    instance.puntos_de_interes.set(puntos_ids)
                except json.JSONDecodeError as e:
                    print("Error al decodificar JSON:", str(e))  # Log para debugging
                    return Response(
                        {'error': f'Error en formato JSON: {str(e)}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Actualizar otros campos
            serializer = self.get_serializer(instance, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            # Manejar nueva multimedia
            multimedia_files = request.FILES.getlist('multimedia')
            if multimedia_files:
                content_type = ContentType.objects.get_for_model(instance)
                for archivo in multimedia_files:
                    MultimediaModel.objects.create(
                        content_type=content_type,
                        object_id=instance.id,
                        archivo=archivo,
                        tipo='foto'
                    )
            
            return Response(serializer.data)
        except Exception as e:
            print("Error en update:", str(e))  # Log para debugging
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class LocalidadModelViewSet(viewsets.ModelViewSet):
    queryset = LocalidadModel.objects.all()
    serializer_class = LocalidadModelSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def agregar_multimedia(self, request, pk=None):
        try:
            localidad = self.get_object()
            archivo = request.FILES.get('archivo')
            titulo = request.data.get('titulo', '')
            descripcion = request.data.get('descripcion', '')
            tipo = request.data.get('tipo', 'foto')  # 'foto' o 'video'

            print(f"Creando multimedia para localidad {localidad.id}")
            
            multimedia = MultimediaModel.objects.create(
                content_type=ContentType.objects.get_for_model(localidad),
                object_id=localidad.id,
                archivo=archivo,
                titulo=titulo,
                descripcion=descripcion,
                tipo=tipo  # Guardar el tipo de multimedia
            )
            
            print(f"Multimedia creada: {multimedia.id}")

            # Actualizar la localidad para incluir la nueva imagen
            serializer = self.get_serializer(localidad, context={'request': request})
            return Response(serializer.data)
            
        except Exception as e:
            print(f"Error al guardar multimedia: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            localidad = serializer.save()
            
            # Manejar la relación de zonas de interés (como ForeignKey)
            zonas_id = request.data.get('zonas_de_interes')
            if zonas_id:
                try:
                    # Si es un string, intentar convertir a entero
                    if isinstance(zonas_id, str) and zonas_id.isdigit():
                        zonas_id = int(zonas_id)
                    zona = ZonasDeInteresModel.objects.get(id=zonas_id)
                    localidad.zonas_de_interes = zona
                    localidad.save()
                except (ValueError, ZonasDeInteresModel.DoesNotExist):
                    pass
                    
            # Manejar la relación de puntos de interés (como ForeignKey)
            puntos_id = request.data.get('puntos_de_interes')
            if puntos_id:
                try:
                    # Si es un string, intentar convertir a entero
                    if isinstance(puntos_id, str) and puntos_id.isdigit():
                        puntos_id = int(puntos_id)
                    punto = PuntoDeInteresModel.objects.get(id=puntos_id)
                    localidad.puntos_de_interes = punto
                    localidad.save()
                except (ValueError, PuntoDeInteresModel.DoesNotExist):
                    pass
                    
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            # Log para verificar los datos guardados
            print("Datos guardados:", serializer.data)

            return Response(serializer.data)
        except Exception as e:
            print("Error al actualizar localidad:", str(e))  # Log de error
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Agregar acción personalizada para eliminar multimedia
    @action(detail=True, methods=['delete'], url_path='multimedia/(?P<multimedia_id>[^/.]+)')
    def eliminar_multimedia(self, request, pk=None, multimedia_id=None):
        try:
            localidad = self.get_object()
            multimedia = localidad.multimedia.filter(id=multimedia_id).first()
            
            if not multimedia:
                return Response(
                    {'message': 'Multimedia no encontrada'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Eliminar el archivo
            if multimedia.archivo:
                multimedia.archivo.delete(save=False)
            
            # Eliminar el registro
            multimedia.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response(
                {'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['DELETE'])
    def eliminar_zonas_de_interes(self, request, pk=None):
        localidad = self.get_object()
        zonas_ids = request.data.get('zonas_ids', [])

        if not zonas_ids:
            return Response({'error': 'No se proporcionaron IDs de zonas'}, status=status.HTTP_400_BAD_REQUEST)

        # Eliminar las zonas de interés
        try:
            for zona_id in zonas_ids:
                zona = ZonasDeInteresModel.objects.get(id=zona_id)
                localidad.zonas_de_interes.remove(zona)

            return Response(status=status.HTTP_204_NO_CONTENT)
        except ZonasDeInteresModel.DoesNotExist:
            return Response({'error': 'Una o más zonas no existen'}, status=status.HTTP_404_NOT_FOUND)

class BarrioModelViewSet(viewsets.ModelViewSet):
    queryset = BarrioModel.objects.all()
    serializer_class = BarrioModelSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=True, methods=['POST'])
    def agregar_multimedia(self, request, pk=None):
        try:
            barrio = self.get_object()
            archivo = request.FILES.get('archivo')
            titulo = request.data.get('titulo', '')
            descripcion = request.data.get('descripcion', '')
            tipo = request.data.get('tipo', 'foto')

            multimedia = MultimediaModel.objects.create(
                content_type=ContentType.objects.get_for_model(barrio),
                object_id=barrio.id,
                archivo=archivo,
                titulo=titulo,
                descripcion=descripcion,
                tipo=tipo
            )

            return Response(
                MultimediaModelSerializer(multimedia, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['DELETE'], url_path='multimedia/(?P<multimedia_id>[^/.]+)')
    def eliminar_multimedia(self, request, pk=None, multimedia_id=None):
        try:
            barrio = self.get_object()
            multimedia = MultimediaModel.objects.get(
                content_type=ContentType.objects.get_for_model(barrio),
                object_id=barrio.id,
                id=multimedia_id
            )
            multimedia.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except MultimediaModel.DoesNotExist:
            return Response(
                {'error': 'Multimedia no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

    def update(self, request, *args, **kwargs):
        try:
            print("Datos recibidos:", request.data)
            instance = self.get_object()
            
            # Crear una copia mutable de los datos
            data = request.data.copy()
            
            # Asegurarse de que localidad sea un ID numérico
            if 'localidad' in data:
                try:
                    # Si es un diccionario u objeto, obtener el ID
                    if isinstance(data['localidad'], dict):
                        data['localidad'] = data['localidad']['id']
                    # Si es una cadena o número, convertir a entero
                    data['localidad'] = int(data['localidad'])
                except (ValueError, TypeError, KeyError):
                    return Response(
                        {'error': 'ID de localidad inválido'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            serializer = self.get_serializer(instance, data=data, partial=True)
            if not serializer.is_valid():
                print("Errores de validación:", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
            self.perform_update(serializer)
            return Response(serializer.data)
        except Exception as e:
            print("Error en update:", str(e))
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    @action(detail=True, methods=['POST'], url_path='agregar-punto-interes')
    def agregar_punto_interes(self, request, pk=None):
        try:
            barrio = self.get_object()
            punto_id = request.data.get('punto_id')
            punto = PuntoDeInteresModel.objects.get(id=punto_id)
            barrio.puntos_de_interes.add(punto)
            return Response({'message': 'Punto de interés agregado correctamente'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'], url_path='agregar-zona-interes')
    def agregar_zona_interes(self, request, pk=None):
        try:
            barrio = self.get_object()
            zona_id = request.data.get('zona_id')
            
            if not zona_id:
                return Response(
                    {'error': 'Se requiere el ID de la zona de interés'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            zona = ZonasDeInteresModel.objects.get(id=zona_id)
            barrio.zonas_de_interes.add(zona)
            
            serializer = self.get_serializer(barrio)
            return Response(serializer.data)
        except ZonasDeInteresModel.DoesNotExist:
            return Response(
                {'error': 'Zona de interés no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['DELETE'], url_path='eliminar-zona-interes/(?P<zona_id>[^/.]+)')
    def eliminar_zona_interes(self, request, pk=None, zona_id=None):
        try:
            barrio = self.get_object()
            zona = ZonasDeInteresModel.objects.get(id=zona_id)
            barrio.zonas_de_interes.remove(zona)
            
            serializer = self.get_serializer(barrio)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class ZonaModelViewSet(viewsets.ModelViewSet):
    queryset = ZonaModel.objects.all()
    serializer_class = ZonaModelSerializer

class EdificioModelViewSet(viewsets.ModelViewSet):
    queryset = EdificioModel.objects.all()
    serializer_class = EdificioModelSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    @action(detail=True, methods=['POST'], url_path='agregar-multimedia')
    def agregar_multimedia(self, request, pk=None):
        try:
            print("Recibiendo solicitud de multimedia")
            edificio = self.get_object()
            archivo = request.FILES.get('archivo')
            titulo = request.data.get('titulo', '')
            descripcion = request.data.get('descripcion', '')
            tipo = request.data.get('tipo', 'foto')

            print(f"Datos recibidos: archivo={archivo}, tipo={tipo}, titulo={titulo}")

            if not archivo:
                return Response(
                    {'error': 'No se proporcionó ningún archivo'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            multimedia = MultimediaModel.objects.create(
                content_type=ContentType.objects.get_for_model(edificio),
                object_id=edificio.id,
                archivo=archivo,
                titulo=titulo,
                descripcion=descripcion,
                tipo=tipo
            )

            print(f"Multimedia creada con ID: {multimedia.id}")
            
            # Devolver la multimedia creada
            return Response(
                MultimediaModelSerializer(multimedia, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            print(f"Error al crear multimedia: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['POST'], url_path='agregar-zona-interes')
    def agregar_zona_interes(self, request, pk=None):
        try:
            edificio = self.get_object()
            zona_id = request.data.get('zona_id')
            
            if not zona_id:
                return Response(
                    {'error': 'Se requiere el ID de la zona de interés'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            zona = ZonasDeInteresModel.objects.get(id=zona_id)
            edificio.zonas_de_interes.add(zona)
            
            serializer = self.get_serializer(edificio)
            return Response(serializer.data)
        except ZonasDeInteresModel.DoesNotExist:
            return Response(
                {'error': 'Zona de interés no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['DELETE'], url_path='eliminar-zona-interes/(?P<zona_id>[^/.]+)')
    def eliminar_zona_interes(self, request, pk=None, zona_id=None):
        try:
            edificio = self.get_object()
            zona = ZonasDeInteresModel.objects.get(id=zona_id)
            edificio.zonas_de_interes.remove(zona)
            
            serializer = self.get_serializer(edificio)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['POST'], url_path='agregar-amenidad')
    def agregar_amenidad(self, request, pk=None):
        try:
            edificio = self.get_object()
            amenidad_id = request.data.get('amenidad_id')
            
            if not amenidad_id:
                return Response(
                    {'error': 'Se requiere el ID de la amenidad'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            amenidad = AmenidadesModel.objects.get(id=amenidad_id)
            edificio.amenidades.add(amenidad)
            
            serializer = self.get_serializer(edificio)
            return Response(serializer.data)
        except AmenidadesModel.DoesNotExist:
            return Response(
                {'error': 'Amenidad no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['DELETE'], url_path='eliminar-amenidad/(?P<amenidad_id>[^/.]+)')
    def eliminar_amenidad(self, request, pk=None, amenidad_id=None):
        try:
            edificio = self.get_object()
            amenidad = AmenidadesModel.objects.get(id=amenidad_id)
            edificio.amenidades.remove(amenidad)
            
            serializer = self.get_serializer(edificio)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        print("Datos recibidos en la vista update:", request.data)
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            
            if not serializer.is_valid():
                print("Errores de validación:", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            edificio = serializer.save()
            print("Edificio actualizado:", edificio)
            print("Amenidades después de actualizar:", list(edificio.amenidades.all()))
            
            return Response(serializer.data)
        except Exception as e:
            print("Error en update:", str(e))
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['DELETE'], url_path='multimedia/(?P<multimedia_id>[^/.]+)')
    def eliminar_multimedia(self, request, pk=None, multimedia_id=None):
        try:
            edificio = self.get_object()
            multimedia = MultimediaModel.objects.get(
                id=multimedia_id,
                content_type=ContentType.objects.get_for_model(edificio),
                object_id=edificio.id
            )
            multimedia.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except MultimediaModel.DoesNotExist:
            return Response(
                {'error': 'Multimedia no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class PropiedadModelViewSet(viewsets.ModelViewSet):
    queryset = PropiedadModel.objects.all()
    serializer_class = PropiedadModelSerializer

    def get_queryset(self):
        queryset = PropiedadModel.objects.all()
        propietario_id = self.request.query_params.get('propietario', None)
        
        if propietario_id is not None:
            queryset = queryset.filter(propietario_id=propietario_id)
        
        return queryset

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if not instance:
                return Response(
                    {'error': 'Propiedad no encontrada'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = self.get_serializer(instance)
            multimedia = MultimediaModel.objects.filter(
                content_type__model='propiedadmodel',
                object_id=instance.id
            )
            multimedia_serializer = MultimediaModelSerializer(
                multimedia, 
                many=True,
                context={'request': request}
            ).data
            
            # Obtener edificios disponibles
            edificios = EdificioModel.objects.all()
            edificios_serializer = EdificioModelSerializer(edificios, many=True).data
            
            return Response({
                'propiedad': serializer.data,
                'amenidades_disponibles': AmenidadesModelSerializer(
                    AmenidadesModel.objects.all(), 
                    many=True
                ).data,
                'multimedia': multimedia_serializer,
                'edificios_disponibles': edificios_serializer
            })
        except Exception as e:
            print(f"Error en retrieve de propiedad: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    def create(self, request, *args, **kwargs):
        try:
            print("\n=== Inicio de creación de propiedad ===")
            print("Datos recibidos:", request.data)
            
            # Validar datos requeridos
            required_fields = ['propietario', 'titulo', 'tipo_propiedad']
            for field in required_fields:
                if field not in request.data:
                    return Response(
                        {field: f"El campo '{field}' es requerido"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                print("Errores de validación:", serializer.errors)
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            propiedad = serializer.save()
            print(f"Propiedad creada: {propiedad}")

            # Guardar amenidades
            amenidades_ids = request.data.get('amenidades', [])
            if amenidades_ids:
                propiedad.amenidades.set(amenidades_ids)  # Asegúrate de que esto esté configurado correctamente
                print(f"Amenidades guardadas: {amenidades_ids}")

            puntos_de_interes_ids = request.data.get('puntos_de_interes', [])
            if puntos_de_interes_ids:
                propiedad.puntos_de_interes.set(puntos_de_interes_ids)
                print(f"Puntos de interés guardados: {puntos_de_interes_ids}")

            zonas_de_interes_ids = request.data.get('zonas_de_interes', [])
            if zonas_de_interes_ids:
                propiedad.zonas_de_interes.set(zonas_de_interes_ids)
                print(f"Zonas de interés guardadas: {zonas_de_interes_ids}")

            return Response(
                self.get_serializer(propiedad).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            print(f"Error en la vista: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Guardar la instancia
        self.perform_update(serializer)

        # Manejar las amenidades
        amenidades_ids = request.data.get('amenidades_ids', [])
        puntos_de_interes_ids = request.data.get('puntos_de_interes_ids', [])
        zonas_de_interes_ids = request.data.get('zonas_de_interes_ids', [])
        print(f"Amenidades IDs recibidos: {amenidades_ids}")  # Debug log
        
        if amenidades_ids is not None:
            instance.amenidades.set(amenidades_ids)
            print(f"Amenidades actualizadas: {instance.amenidades.all()}")  # Debug log

        if puntos_de_interes_ids is not None:
            instance.puntos_de_interes.set(puntos_de_interes_ids)
            print(f"Puntos de interés actualizados: {instance.puntos_de_interes.all()}")  # Debug log

        if zonas_de_interes_ids is not None:
            instance.zonas_de_interes.set(zonas_de_interes_ids)
            print(f"Zonas de interés actualizadas: {instance.zonas_de_interes.all()}")  # Debug log

        # Obtener la instancia actualizada
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def agregar_imagen(self, request, pk=None):
        print("Headers recibidos:", request.headers)
        print("FILES recibidos:", request.FILES)
        print("POST data:", request.POST)
        try:
            propiedad = self.get_object()
            archivo = request.FILES.get('archivo')
            
            # Agregar logging
            print(f"Archivo recibido: {archivo}")
            print(f"Nombre del archivo: {archivo.name if archivo else 'No archivo'}")
            
            multimedia = MultimediaModel.objects.create(
                content_type=ContentType.objects.get_for_model(propiedad),
                object_id=propiedad.id,
                archivo=archivo
            )
            
            # Verificar URL generada
            print(f"URL generada: {multimedia.archivo.url}")
            
            return Response(MultimediaModelSerializer(
                multimedia, 
                context={'request': request}
            ).data)
        except Exception as e:
            print(f"Error al guardar imagen: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['POST'])
    def generate_ai_description(self, request, pk=None):
        try:
            propiedad = self.get_object()
            ai_service = AIService()
            
            # Serializar la propiedad para enviar a OpenAI
            serializer = self.get_serializer(propiedad)
            result = ai_service.generate_property_description(serializer.data)
            
            if result["success"]:
                return Response({
                    "description": result["description"]
                })
            else:
                return Response(
                    {"error": result["error"]},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RequerimientoModelViewSet(viewsets.ModelViewSet):
    queryset = RequerimientoModel.objects.all()
    serializer_class = RequerimientoModelSerializer

class TareaModelViewSet(viewsets.ModelViewSet):
    queryset = TareaModel.objects.all()
    serializer_class = TareaModelSerializer

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['POST'])
    def seguimiento(self, request, pk=None):
        try:
            tarea = self.get_object()
            
            # Crear el seguimiento
            seguimiento_data = {
                'tarea': tarea,
                'descripcion': request.data.get('descripcion'),
                'estado': request.data.get('estado'),
                'notas_internas': request.data.get('notas_internas'),
                'resultado': request.data.get('resultado')
            }

            # Si hay archivo adjunto
            if 'archivos_adjuntos' in request.FILES:
                seguimiento_data['archivos_adjuntos'] = request.FILES['archivos_adjuntos']

            seguimiento = FaseSeguimientoModel.objects.create(**seguimiento_data)
            
            return Response(
                FaseSeguimientoModelSerializer(seguimiento).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Obtener los seguimientos relacionados
        seguimientos = instance.fases.all()  # Asumiendo que 'fases' es el related_name en el modelo
        seguimientos_serializer = FaseSeguimientoModelSerializer(seguimientos, many=True).data
        
        # Incluir los seguimientos en la respuesta
        return Response({
            'tarea': serializer.data,
            'seguimientos': seguimientos_serializer
        })

@api_view(['POST'])
def transcribe_audio(request):
    try:
        audio_file = request.FILES.get('audio')
        if not audio_file:
            return Response(
                {'error': 'No se proporcionó archivo de audio'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Guardar el archivo temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_audio:
            for chunk in audio_file.chunks():
                temp_audio.write(chunk)
            temp_audio_path = temp_audio.name

        try:
            # Usar el servicio AI para transcribir
            ai_service = AIService()
            result = ai_service.client.audio.transcriptions.create(
                model="whisper-1",
                file=open(temp_audio_path, "rb")
            )

            # Modificación aquí: accedemos al texto directamente
            return Response({'text': result.text})  # Cambiamos result por result.text

        finally:
            # Limpiar el archivo temporal
            try:
                os.unlink(temp_audio_path)
            except Exception as e:
                print(f"Error al eliminar archivo temporal: {e}")

    except Exception as e:
        print(f"Error en transcribe_audio: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def analyze_image(request):
    try:
        image_file = request.FILES.get('image')
        analysis_type = request.POST.get('analysis_type', 'ocr')  # 'ocr' o 'property'
        
        if not image_file:
            return Response(
                {'error': 'No se proporcionó archivo de imagen'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_image:
            for chunk in image_file.chunks():
                temp_image.write(chunk)
            temp_image_path = temp_image.name

        try:
            ai_service = AIService()
            result = ai_service.analyze_image(temp_image_path, analysis_type)
            return Response({'text': result})
        finally:
            try:
                os.unlink(temp_image_path)
            except Exception as e:
                print(f"Error al eliminar archivo temporal: {e}")

    except Exception as e:
        print(f"Error en analyze_image: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class PuntoDeInteresModelViewSet(viewsets.ModelViewSet):
    queryset = PuntoDeInteresModel.objects.all()
    serializer_class = PuntoDeInteresModelSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def create(self, request, *args, **kwargs):
        try:
            # Obtener los datos básicos
            data = request.data.copy()
            
            # Crear el punto de interés
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            punto = serializer.save()

            # Manejar archivos multimedia
            multimedia_files = request.FILES.getlist('multimedia')
            for archivo in multimedia_files:
                tipo = 'video' if archivo.content_type.startswith('video/') else 'foto'
                MultimediaModel.objects.create(
                    content_type=ContentType.objects.get_for_model(punto),
                    object_id=punto.id,
                    archivo=archivo,
                    tipo=tipo  # Determinar el tipo según el archivo
                )

            # Obtener el objeto actualizado con toda la multimedia
            serializer = self.get_serializer(punto)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['POST'])
    def agregar_multimedia(self, request, pk=None):
        try:
            punto = self.get_object()
            archivo = request.FILES.get('archivo')
            titulo = request.data.get('titulo', '')
            descripcion = request.data.get('descripcion', '')
            tipo = request.data.get('tipo', 'foto')

            multimedia = MultimediaModel.objects.create(
                content_type=ContentType.objects.get_for_model(punto),
                object_id=punto.id,
                archivo=archivo,
                titulo=titulo,
                descripcion=descripcion,
                tipo=tipo
            )

            serializer = self.get_serializer(punto)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['DELETE'], url_path='multimedia/(?P<multimedia_id>[^/.]+)')
    def eliminar_multimedia(self, request, pk=None, multimedia_id=None):
        try:
            punto = self.get_object()
            multimedia = MultimediaModel.objects.get(
                content_type=ContentType.objects.get_for_model(punto),
                object_id=punto.id,
                id=multimedia_id
            )
            multimedia.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except MultimediaModel.DoesNotExist:
            return Response(
                {'error': 'Multimedia no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

    def update(self, request, *args, **kwargs):
        try:
            punto = self.get_object()
            
            # Actualizar campos básicos
            serializer = self.get_serializer(punto, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            punto = serializer.save()

            # Manejar archivos multimedia
            multimedia_files = request.FILES.getlist('multimedia')
            for archivo in multimedia_files:
                tipo = 'video' if archivo.content_type.startswith('video/') else 'foto'
                MultimediaModel.objects.create(
                    content_type=ContentType.objects.get_for_model(punto),
                    object_id=punto.id,
                    archivo=archivo,
                    tipo=tipo
                )

            # Obtener el objeto actualizado con toda la multimedia
            serializer = self.get_serializer(punto)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

@api_view(['POST'])
def generate_image(request):
    try:
        dimensions = request.data.get('dimensions', 1024)
        style = request.data.get('style', 'icon')
        prompt = request.data.get('prompt', '')
        colors = request.data.get('colors', None)
        quality = request.data.get('quality', 'standard')

        from .IA.img_generator import AIService
        ai_service = AIService()
        result = ai_service.generate_image(dimensions, style, prompt, colors, quality)

        if result["success"]:
            # Descargar la imagen y convertirla a base64
            response = requests.get(result["image_url"])
            if response.status_code == 200:
                image_base64 = base64.b64encode(response.content).decode('utf-8')
                return Response({
                    "success": True,
                    "image_url": result["image_url"],
                    "image_base64": image_base64
                })
            else:
                return Response({
                    "error": "No se pudo descargar la imagen"
                }, status=500)
        else:
            return Response({"error": result["error"]}, status=500)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

class AgendaModelViewSet(viewsets.ModelViewSet):
    queryset = AgendaModel.objects.all()
    serializer_class = AgendaModelSerializer
    
    def get_queryset(self):
        """
        Filtra las agendas según el cliente especificado en los parámetros de consulta.
        """
        queryset = AgendaModel.objects.all()
        cliente_id = self.request.query_params.get('cliente', None)
        
        if cliente_id is not None:
            queryset = queryset.filter(cliente_id=cliente_id)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """
        Crea una nueva agenda.
        """
        print("Datos recibidos para crear agenda:", request.data)
        
        # Validar datos requeridos
        required_fields = ['cliente', 'agente', 'fecha', 'hora']
        for field in required_fields:
            if field not in request.data:
                return Response(
                    {field: f"El campo '{field}' es requerido"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            print(f"Agenda creada: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Error al crear agenda: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
@csrf_exempt
def requerimientoAgentView(request):
    """Vista para manejar la conversación con el agente de requerimientos inmobiliarios."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action', '')
            
            # Mejorar el log para depuración
            print(f"RequerimientoAgentView: Action={action}, Data={data}")
            
            # Verificar si se proporcionaron IDs de cliente y agente
            if action == 'iniciar':
                # Obtener IDs (usar valores por defecto si no se proporcionan)
                cliente_id = data.get('cliente_id', 29)
                if cliente_id is None:
                    print("Error: El ID del cliente es nulo. Usando valor por defecto: 29")
                    cliente_id = 29
                
                agente_id = data.get('agente_id', 12)
                if agente_id is None:
                    print("Error: El ID del agente es nulo. Usando valor por defecto: 12")
                    agente_id = 12
                
                print(f"Iniciando conversación con Cliente ID: {cliente_id}, Agente ID: {agente_id}")
                
                # Configurar los IDs en el agente
                agente.set_ids(cliente_id=cliente_id, agente_id=agente_id)
                
                # Reiniciar el agente para una nueva conversación
                agente.reset()
                response = agente.procesar_mensaje('')
                return JsonResponse(response)
            
            elif action == 'mensaje':
                mensaje = data.get('mensaje', '')
                response = agente.procesar_mensaje(mensaje)
                return JsonResponse(response)
            
            elif action == 'confirmar':
                confirmacion = data.get('confirmacion', False)
                response = agente.confirmar_resumen(confirmacion)
                return JsonResponse(response)
            
            elif action == 'modificar':
                aspectos = data.get('aspectos', 'todos')
                response = agente.modificar_aspectos(aspectos)
                return JsonResponse(response)
            
            else:
                return JsonResponse({'error': 'Acción no reconocida'}, status=400)
                
        except Exception as e:
            print(f"Error al procesar la solicitud: {str(e)}")
            return JsonResponse({'error': f"Error al procesar la solicitud: {str(e)}"}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@api_view(['GET', 'POST'])
def requerimientoAIView(request):
    print("Llamada a requerimientoAIView con método:", request.method)
    
    if request.method == 'POST':
        print("Procesando solicitud POST para crear un nuevo requerimiento.")
        
        # Capturar la información del nuevo requerimiento
        data = request.data
        print("Datos recibidos:", data)
        
        # Validar que los campos obligatorios estén presentes
        if 'agente' not in data or 'cliente' not in data:
            print("Error: Los campos 'agente' y 'cliente' son obligatorios y no están presentes.")
            return Response(
                {"error": "Los campos 'agente' y 'cliente' son obligatorios"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Asegurarse de que tipo_negocio sea un JSON válido
        if 'tipo_negocio' in data and isinstance(data['tipo_negocio'], str):
            try:
                data['tipo_negocio'] = json.loads(data['tipo_negocio'])
                print("tipo_negocio convertido a JSON válido:", data['tipo_negocio'])
            except json.JSONDecodeError:
                # Si no es un JSON válido, convertirlo a un formato válido
                data['tipo_negocio'] = {"tipo": data['tipo_negocio']}
                print("tipo_negocio no era un JSON válido, convertido a formato válido:", data['tipo_negocio'])
        
        # Convertir campos numéricos si vienen como strings
        numeric_fields = ['habitantes', 'area_minima', 'habitaciones', 'banos', 'parqueaderos']
        for field in numeric_fields:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = int(data[field])
                    print(f"Campo '{field}' convertido a entero:", data[field])
                except ValueError:
                    print(f"Error: El campo '{field}' debe ser un número entero.")
                    return Response(
                        {"error": f"El campo '{field}' debe ser un número entero"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        # Convertir campos decimales si vienen como strings
        decimal_fields = ['presupuesto_minimo', 'presupuesto_maximo', 
                         'presupuesto_minimo_compra', 'presupuesto_maximo_compra']
        for field in decimal_fields:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = float(data[field])
                    print(f"Campo '{field}' convertido a decimal:", data[field])
                except ValueError:
                    print(f"Error: El campo '{field}' debe ser un número decimal.")
                    return Response(
                        {"error": f"El campo '{field}' debe ser un número decimal. Por favor, asegúrate de que el valor proporcionado sea un número válido."}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        # Crear el serializer con los datos validados
        serializer = RequerimientoModelSerializer(data=data)
        print("Serializer creado con los datos validados.")
        
        if serializer.is_valid():
            serializer.save()  # Guardar el nuevo requerimiento en la base de datos
            print("Nuevo requerimiento guardado exitosamente.")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        print("Errores de validación en el serializer:", serializer.errors)
        return Response({"error": "Errores de validación en los datos proporcionados.", "detalles": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    # Si es una solicitud GET, podríamos devolver un formulario o documentación
    print("Solicitud GET recibida. Instrucciones para el usuario.")
    return Response({"message": "Usa POST para crear un nuevo requerimiento"})

@csrf_exempt
def propiedadAgentView(request):
    """Vista para manejar la conversación con el agente de registro de propiedades."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action', '')
            
            # Mejorar el log para depuración
            print(f"PropiedadAgentView: Action={action}, Data={data}")
            
            # Verificar si se proporcionaron IDs
            if action == 'iniciar':
                # Obtener IDs (usar valores por defecto si no se proporcionan)
                agente_id = data.get('agente_id', 12)
                if agente_id is None:
                    print("Error: El ID del agente es nulo. Usando valor por defecto: 12")
                    agente_id = 12
                
                propietario_id = data.get('propietario_id')
                print(f"Iniciando conversación con Agente ID: {agente_id}, Propietario ID: {propietario_id}")
                
                # Configurar los IDs en el agente
                agente_propiedad.set_ids(agente_id=agente_id, propietario_id=propietario_id)
                
                # Reiniciar el agente para una nueva conversación
                agente_propiedad.reset()
                response = agente_propiedad.procesar_mensaje('')
                return JsonResponse(response)
            
            elif action == 'mensaje':
                mensaje = data.get('mensaje', '')
                response = agente_propiedad.procesar_mensaje(mensaje)
                return JsonResponse(response)
            
            elif action == 'confirmar':
                confirmacion = data.get('confirmacion', False)
                response = agente_propiedad.confirmar_resumen(confirmacion)
                return JsonResponse(response)
            
            elif action == 'modificar':
                aspectos = data.get('aspectos', 'todos')
                response = agente_propiedad.modificar_aspectos(aspectos)
                return JsonResponse(response)
            
            else:
                return JsonResponse({'error': 'Acción no reconocida'}, status=400)
                
        except Exception as e:
            print(f"Error al procesar la solicitud: {str(e)}")
            return JsonResponse({'error': f"Error al procesar la solicitud: {str(e)}"}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@api_view(['GET', 'POST'])
def propiedadAIView(request):
    print("Llamada a propiedadAIView con método:", request.method)
    
    if request.method == 'POST':
        print("Procesando solicitud POST para crear una nueva propiedad.")
        
        # Capturar la información de la nueva propiedad
        data = request.data
        print("Datos recibidos:", data)
        
        # Validar que el campo agente esté presente
        if 'agente' not in data:
            print("Error: El campo 'agente' es obligatorio y no está presente.")
            return Response(
                {"error": "El campo 'agente' es obligatorio"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Asegurarse de que modalidad_de_negocio sea un JSON válido
        if 'modalidad_de_negocio' in data and isinstance(data['modalidad_de_negocio'], str):
            try:
                data['modalidad_de_negocio'] = json.loads(data['modalidad_de_negocio'])
                print("modalidad_de_negocio convertido a JSON válido:", data['modalidad_de_negocio'])
            except json.JSONDecodeError:
                # Si no es un JSON válido, convertirlo a un formato válido
                data['modalidad_de_negocio'] = {"operacion": data['modalidad_de_negocio']}
                print("modalidad_de_negocio no era un JSON válido, convertido a formato válido:", data['modalidad_de_negocio'])
        
        # Asegurarse de que direccion sea un JSON válido
        if 'direccion' in data and isinstance(data['direccion'], str):
            try:
                data['direccion'] = json.loads(data['direccion'])
                print("direccion convertido a JSON válido:", data['direccion'])
            except json.JSONDecodeError:
                # Si no es un JSON válido, convertirlo a un formato válido
                data['direccion'] = {"direccion": data['direccion']}
                print("direccion no era un JSON válido, convertido a formato válido:", data['direccion'])
        
        # Asegurarse de que garajes y depositos sean JSON válidos
        for field in ['garajes', 'depositos']:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = json.loads(data[field])
                    print(f"{field} convertido a JSON válido:", data[field])
                except json.JSONDecodeError:
                    # Si no es un JSON válido, intentar extraer un número
                    import re
                    match = re.search(r'\d+', data[field])
                    if match:
                        cantidad = match.group(0)
                        data[field] = {"cantidad": cantidad}
                        print(f"{field} no era un JSON válido, convertido a formato válido:", data[field])
                    else:
                        data[field] = {"cantidad": "1"}
        
        # Convertir campos numéricos si vienen como strings
        numeric_fields = ['nivel', 'metro_cuadrado_construido', 'metro_cuadrado_propiedad',
                         'habitaciones', 'habitacion_de_servicio', 'banos']
        for field in numeric_fields:
            if field in data and isinstance(data[field], str):
                try:
                    # Intentar extraer un número si el campo contiene texto
                    import re
                    match = re.search(r'\d+', data[field])
                    if match:
                        data[field] = int(match.group(0))
                    else:
                        data[field] = int(data[field])
                    print(f"Campo '{field}' convertido a entero:", data[field])
                except ValueError:
                    print(f"Error: El campo '{field}' debe ser un número entero.")
                    # Establecer valor por defecto en lugar de retornar error
                    if field in ['habitaciones', 'banos', 'nivel']:
                        data[field] = 0
                    else:
                        data[field] = None
        
        # Normalizar campos de selección
        for field in ['terraza', 'balcon', 'mascotas']:
            if field in data and isinstance(data[field], str):
                if data[field].lower() in ['sí', 'si', 'yes', 'y', 'true', '1']:
                    data[field] = 'si'
                else:
                    data[field] = 'no'
        
        # Crear el serializer con los datos validados
        serializer = PropiedadModelSerializer(data=data)
        print("Serializer creado con los datos validados.")
        
        if serializer.is_valid():
            serializer.save()  # Guardar la nueva propiedad en la base de datos
            print("Nueva propiedad guardada exitosamente.")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        print("Errores de validación en el serializer:", serializer.errors)
        return Response({"error": "Errores de validación en los datos proporcionados.", "detalles": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    # Si es una solicitud GET, podríamos devolver un formulario o documentación
    print("Solicitud GET recibida. Instrucciones para el usuario.")
    return Response({"message": "Usa POST para crear una nueva propiedad"})

@csrf_exempt
def agendaAbiertaView(request):
    """Vista para que los agentes puedan abrir una nueva agenda o listar agendas existentes."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            serializer = AgendaAbiertaModelSerializer(data=data)
            
            if serializer.is_valid():
                serializer.save()  # Guardar la nueva agenda en la base de datos
                return JsonResponse(serializer.data, status=201)  # Retornar el objeto creado
            return JsonResponse(serializer.errors, status=400)  # Retornar errores de validación
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)  # Manejo de errores

    elif request.method == 'GET':
        try:
            agendas = AgendaAbiertaModel.objects.all()  # Obtener todas las agendas
            serializer = AgendaAbiertaModelSerializer(agendas, many=True)  # Serializar las agendas
            return JsonResponse(serializer.data, safe=False)  # Retornar las agendas como JSON
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)  # Manejo de errores

    return JsonResponse({'error': 'Método no permitido'}, status=405)  # Manejo de métodos no permitidos

@csrf_exempt
def agendaAgentView(request):
    """Vista para manejar la conversación con el agente de agendas."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action', '')
            
            agente = AgenteAgenda()
            
            if action == 'iniciar':
                agente.reset()
                response = agente.procesar_mensaje('')
                return JsonResponse(response)
            
            elif action == 'mensaje':
                mensaje = data.get('mensaje', '')
                response = agente.procesar_mensaje(mensaje)
                return JsonResponse(response)
            
            else:
                return JsonResponse({'error': 'Acción no reconocida'}, status=400)
                
        except Exception as e:
            return JsonResponse({'error': f"Error al procesar la solicitud: {str(e)}"}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)