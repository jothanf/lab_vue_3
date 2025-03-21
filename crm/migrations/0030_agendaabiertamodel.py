# Generated by Django 5.0.2 on 2025-03-18 22:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_clientemodel_cedula'),
        ('crm', '0029_alter_requerimientomodel_agente_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgendaAbiertaModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('hora', models.TimeField()),
                ('agente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.agentemodel')),
            ],
        ),
    ]
