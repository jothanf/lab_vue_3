# Generated by Django 5.0.2 on 2024-12-18 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0020_edificiomodel_estado_edificiomodel_tipo_edificio'),
    ]

    operations = [
        migrations.AddField(
            model_name='barriomodel',
            name='zonas_de_interes',
            field=models.ManyToManyField(blank=True, related_name='barrios', to='crm.zonasdeinteresmodel'),
        ),
    ]