from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AmenidadesModelViewSet, CaracteristicasInterioresModelViewSet, ZonasDeInteresModelViewSet, LocalidadModelViewSet, BarrioModelViewSet, ZonaModelViewSet, EdificioModelViewSet, PropiedadModelViewSet, RequerimientoModelViewSet, TareaModelViewSet, transcribe_audio, analyze_image, PuntoDeInteresModelViewSet
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'amenidades', AmenidadesModelViewSet)
router.register(r'caracteristicasInteriores', CaracteristicasInterioresModelViewSet)
router.register(r'zonasDeInteres', ZonasDeInteresModelViewSet)
router.register(r'localidades', LocalidadModelViewSet)
router.register(r'barrio', BarrioModelViewSet)
router.register(r'zona', ZonaModelViewSet)
router.register(r'edificios', EdificioModelViewSet)
router.register(r'propiedades', PropiedadModelViewSet)
router.register(r'requerimientos', RequerimientoModelViewSet)
router.register(r'tareas', TareaModelViewSet)
router.register(r'puntos-de-interes', PuntoDeInteresModelViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('transcribe-audio/', transcribe_audio, name='transcribe-audio'),
    path('analyze-image/', analyze_image, name='analyze-image'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
