# Generated by Django 5.0.2 on 2024-12-11 22:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0004_alter_zonamodel_options_remove_zonamodel_localidad_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='edificiomodel',
            name='localidad',
        ),
        migrations.RemoveField(
            model_name='edificiomodel',
            name='zona',
        ),
        migrations.AlterField(
            model_name='edificiomodel',
            name='direccion',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='edificiomodel',
            name='telefono',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='edificiomodel',
            name='ubicacion',
            field=models.JSONField(help_text='\n        {\n            "latitud": "1234567890",\n            "longitud": "0987654321"\n        }\n    ', max_length=255),
        ),
    ]
