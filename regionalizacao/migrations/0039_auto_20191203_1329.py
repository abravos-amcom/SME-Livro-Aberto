# Generated by Django 2.2.7 on 2019-12-03 13:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('regionalizacao', '0038_recurso'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='recurso',
            unique_together={('budget', 'subgrupo')},
        ),
    ]
