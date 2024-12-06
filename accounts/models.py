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
    