# Generated by Django 5.0.2 on 2024-12-11 23:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_clientemodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientemodel',
            name='estado_del_cliente',
            field=models.CharField(blank=True, help_text="\n        choices=[\n            ('activo', 'Activo'),\n            ('inactivo', 'Inactivo'),\n        ]\n    ", max_length=100, null=True),
        ),
        migrations.AlterModelTable(
            name='clientemodel',
            table=None,
        ),
    ]
