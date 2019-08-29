# Generated by Django 2.2.3 on 2019-08-12 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contratos', '0025_auto_20190808_1635'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contratoraw',
            name='datAssinaturaContrato',
            field=models.CharField(blank=True, db_column='datassinaturacontrato', max_length=26, null=True),
        ),
        migrations.AlterField(
            model_name='contratoraw',
            name='datPublicacaoContrato',
            field=models.CharField(blank=True, db_column='datpublicacaocontrato', max_length=26, null=True),
        ),
        migrations.AlterField(
            model_name='contratoraw',
            name='datVigenciaContrato',
            field=models.CharField(blank=True, db_column='datvigencia', max_length=26, null=True),
        ),
        migrations.AlterField(
            model_name='contratoraw',
            name='dataExtracaoContrato',
            field=models.CharField(blank=True, db_column='data_extracao', max_length=26, null=True),
        ),
    ]