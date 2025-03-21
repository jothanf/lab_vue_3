# Generated by Django 5.0.2 on 2025-03-13 21:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_clientemodel_cedula'),
        ('crm', '0027_barriomodel_puntos_de_interes_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgendaModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('hora', models.TimeField()),
                ('estado', models.CharField(default='pendiente', max_length=20)),
                ('notas', models.TextField(blank=True, null=True)),
                ('agente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.agentemodel')),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.clientemodel')),
                ('propiedad', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='crm.propiedadmodel')),
            ],
        ),
    ]
