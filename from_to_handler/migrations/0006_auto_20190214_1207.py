# Generated by Django 2.1.5 on 2019-02-14 12:07

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('from_to_handler', '0005_auto_20190214_1206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dotacaofromtospreadsheet',
            name='added_fromtos',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=28), editable=False, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='dotacaofromtospreadsheet',
            name='not_added_fromtos',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=28), editable=False, null=True, size=None),
        ),
    ]
