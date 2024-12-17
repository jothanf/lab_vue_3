# Generated by Django 5.0.2 on 2024-12-06 19:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClienteModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_ingreso', models.DateTimeField(auto_now_add=True)),
                ('nombre', models.CharField(blank=True, max_length=100, null=True)),
                ('apellidos', models.CharField(blank=True, max_length=100, null=True)),
                ('telefono', models.CharField(blank=True, max_length=20, null=True)),
                ('telefono_secundario', models.CharField(blank=True, max_length=20, null=True)),
                ('correo', models.EmailField(blank=True, max_length=100, null=True)),
                ('cedula', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('password', models.CharField(default='0000', max_length=255)),
                ('canal_ingreso', models.CharField(blank=True, max_length=100, null=True)),
                ('estado_del_cliente', models.CharField(blank=True, max_length=100, null=True)),
                ('notas', models.TextField(blank=True, null=True)),
                ('agente', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clientes_asignados', to='accounts.agentemodel')),
            ],
            options={
                'db_table': 'clientes',
            },
        ),
    ]