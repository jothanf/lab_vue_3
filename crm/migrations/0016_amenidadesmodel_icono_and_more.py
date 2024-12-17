# Generated by Django 5.0.2 on 2024-12-15 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0015_remove_localidadmodel_zonas_de_interes_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='amenidadesmodel',
            name='icono',
            field=models.ImageField(blank=True, null=True, upload_to='iconos/amenidades/'),
        ),
        migrations.AddField(
            model_name='caracteristicasinterioresmodel',
            name='icono',
            field=models.ImageField(blank=True, null=True, upload_to='iconos/caracteristicas/'),
        ),
        migrations.AddField(
            model_name='zonasdeinteresmodel',
            name='icono',
            field=models.ImageField(blank=True, null=True, upload_to='iconos/zonas/'),
        ),
    ]
