# Generated by Django 5.0.2 on 2024-12-13 04:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0012_propiedadmodel_honorarios'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='propiedadmodel',
            name='amenidades',
        ),
        migrations.AddField(
            model_name='propiedadmodel',
            name='amenidades',
            field=models.ManyToManyField(blank=True, to='crm.amenidadesmodel'),
        ),
    ]
