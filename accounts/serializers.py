from rest_framework import serializers
from django.contrib.auth.models import User
from .models import AgenteModel, ClienteModel

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }

class AgenteSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = AgenteModel
        fields = '__all__'

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password = user_data.pop('password')
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=password,
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', '')
        )
        agente = AgenteModel.objects.create(user=user, **validated_data)
        return agente

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClienteModel
        fields = '__all__'

class ClienteRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = ClienteModel
        fields = ('email', 'password', 'nombre', 'apellidos', 'telefono', 
                  'telefono_secundario', 'cedula', 'canal_ingreso', 'estado_del_cliente')
        
    def create(self, validated_data):
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        
        # Crear un usuario para el cliente
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=validated_data.get('nombre', ''),
            last_name=validated_data.get('apellidos', '')
        )
        
        # Crear el cliente
        cliente = ClienteModel.objects.create(
            correo=email,
            **validated_data
        )
        
        return cliente
