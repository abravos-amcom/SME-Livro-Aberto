# Generated by Django 3.1.1 on 2020-10-05 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regionalizacao', '0054_auto_20201005_1551'),
    ]

    operations = [
        migrations.AddField(
            model_name='unidadevaloresverbafromto',
            name='data_do_encerramento',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='unidadevaloresverbafromto',
            name='situacao',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]