# Generated by Django 2.2.6 on 2019-11-17 22:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('regionalizacao', '0011_auto_20191117_2154'),
    ]

    operations = [
        migrations.RenameField(
            model_name='distritozonafromtospreadsheet',
            old_name='not_added_fromtos',
            new_name='updated_fromtos',
        ),
        migrations.RenameField(
            model_name='etapatipoescolafromtospreadsheet',
            old_name='not_added_fromtos',
            new_name='updated_fromtos',
        ),
        migrations.RenameField(
            model_name='ptrffromtospreadsheet',
            old_name='not_added_fromtos',
            new_name='updated_fromtos',
        ),
        migrations.RenameField(
            model_name='unidaderecursosfromtospreadsheet',
            old_name='not_added_fromtos',
            new_name='updated_fromtos',
        ),
    ]