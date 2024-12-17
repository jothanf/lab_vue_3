from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class AgenteModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]
    
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]

    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='user')
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    telefono = models.CharField(max_length=20)
    cedula = models.CharField(max_length=20, unique=True, null=True, blank=True)
    zona_especializacion = models.IntegerField(null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='activo')

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}" if self.user else "Agente sin usuario"
  
class ClienteModel(models.Model):
    agente = models.ForeignKey(
        AgenteModel, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='clientes_asignados'
    )
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    nombre = models.CharField(max_length=100, null=True, blank=True)
    apellidos = models.CharField(max_length=100, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    telefono_secundario = models.CharField(max_length=20, null=True, blank=True)
    correo = models.EmailField(max_length=100, null=True, blank=True)
    cedula = models.CharField(max_length=20, null=True, blank=True)
    password = models.CharField(max_length=255, default='0000')
    canal_ingreso = models.CharField(max_length=100, null=True, blank=True)
    estado_del_cliente = models.CharField(max_length=100, null=True, blank=True, help_text="""
        choices=[
            ('activo', 'Activo'),
            ('inactivo', 'Inactivo'),
        ]
    """ )
    notas = models.TextField(null=True, blank=True)

    