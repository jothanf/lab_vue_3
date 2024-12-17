from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import AgenteModel, ClienteModel
from .serializers import AgenteSerializer, ClienteSerializer
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, UserSerializer
from django.contrib.auth.models import User
from rest_framework.decorators import action

# Create your views here.

class AgenteModelViewSet(viewsets.ModelViewSet):
    queryset = AgenteModel.objects.all()
    serializer_class = AgenteSerializer

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return Response({'data': response.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
            return Response({'data': response.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            response = super().destroy(request, *args, **kwargs)
            return Response({'data': response.data}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def clientes(self, request, pk=None):
        try:
            agente = self.get_object()
            # Suponiendo que quieres obtener todos los clientes asociados a este agente
            clientes = ClienteModel.objects.filter(agente=agente)
            serializer = ClienteSerializer(clientes, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ClienteModelViewSet(viewsets.ModelViewSet):
    queryset = ClienteModel.objects.all()
    serializer_class = ClienteSerializer

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return Response({'data': response.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
            return Response({'data': response.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            response = super().destroy(request, *args, **kwargs)
            return Response({'data': response.data}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

@api_view(['POST'])
def login_view(request):
    try:
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            # Intenta autenticar primero con el username
            user = authenticate(username=username, password=password)
            
            # Si no funciona, intenta con el email
            if user is None:
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None
            
            if user is not None:
                refresh = RefreshToken.for_user(user)
                agente = AgenteModel.objects.get(user=user)
                return Response({
                    'token': str(refresh.access_token),
                    'user': UserSerializer(user).data,
                    'role': agente.role
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Credenciales inválidas'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        print(f"Error en login: {str(e)}")
        return Response({
            'error': 'Error en el servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
