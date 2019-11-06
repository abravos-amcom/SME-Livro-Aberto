# Generated by Django 2.2.6 on 2019-11-06 16:04

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DistritoZonaFromToSpreadsheet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spreadsheet', models.FileField(upload_to='regionalizacao/fromto_spreadsheets', verbose_name='Planilha')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('extracted', models.BooleanField(default=False, editable=False)),
                ('added_fromtos', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=28), editable=False, null=True, size=None)),
                ('not_added_fromtos', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=28), editable=False, null=True, size=None)),
            ],
            options={
                'verbose_name': 'Planilha De-Para: Distrito-Zona',
                'verbose_name_plural': 'Planilhas De-Para: Distrito-Zona',
            },
        ),
    ]
