# Generated by Django 2.2.3 on 2019-08-07 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contratos', '0021_auto_20190804_2046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoriacontrato',
            name='name',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]