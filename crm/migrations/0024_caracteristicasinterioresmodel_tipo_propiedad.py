# Generated by Django 5.0.2 on 2024-12-21 00:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0023_requerimientomodel_negocibles_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='caracteristicasinterioresmodel',
            name='tipo_propiedad',
            field=models.CharField(blank=True, help_text='\n        apartamento, casa, lote\n    ', max_length=100, null=True),
        ),
    ]
