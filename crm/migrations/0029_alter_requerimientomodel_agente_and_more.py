# Generated by Django 5.0.2 on 2025-03-18 03:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_clientemodel_cedula'),
        ('crm', '0028_agendamodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requerimientomodel',
            name='agente',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.agentemodel'),
        ),
        migrations.AlterField(
            model_name='requerimientomodel',
            name='cliente',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.clientemodel'),
        ),
    ]
