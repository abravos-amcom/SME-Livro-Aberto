# Generated by Django 2.2.3 on 2019-08-04 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contratos', '0017_auto_20190804_1800'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contratoraw',
            name='numoriginalcontrato',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='contratoraw',
            name='txtdescricaomodalidade',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='contratoraw',
            name='txtdescricaoorgao',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='contratoraw',
            name='txtobjetocontrato',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='contratoraw',
            name='txtrazaosocial',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='contratoraw',
            name='txttipocontratacao',
            field=models.TextField(blank=True, null=True),
        ),
    ]