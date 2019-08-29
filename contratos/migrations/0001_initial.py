# Generated by Django 2.2.3 on 2019-07-13 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ContratosRawLoad',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('anoexercicio', models.IntegerField(blank=True, null=True)),
                ('codcontrato', models.IntegerField(blank=True, null=True)),
                ('codempresa', models.IntegerField(blank=True, null=True)),
                ('codmodalidade', models.IntegerField(blank=True, null=True)),
                ('codorgao', models.IntegerField(blank=True, null=True)),
                ('codprocesso', models.BigIntegerField(blank=True, null=True)),
                ('codtipocontratacao', models.IntegerField(blank=True, null=True)),
                ('datassinaturacontrato', models.DateField(blank=True, null=True)),
                ('datpublicacaocontrato', models.DateField(blank=True, null=True)),
                ('datvigencia', models.DateField(blank=True, null=True)),
                ('numoriginalcontrato', models.CharField(blank=True, max_length=20, null=True)),
                ('txtdescricaomodalidade', models.CharField(blank=True, max_length=21, null=True)),
                ('txtdescricaoorgao', models.CharField(blank=True, max_length=32, null=True)),
                ('txtobjetocontrato', models.CharField(blank=True, max_length=1000, null=True)),
                ('txtrazaosocial', models.CharField(blank=True, max_length=36, null=True)),
                ('txttipocontratacao', models.CharField(blank=True, max_length=67, null=True)),
                ('valaditamentos', models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True)),
                ('valanulacao', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('valanuladoempenho', models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True)),
                ('valempenhadoliquido', models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True)),
                ('valliquidado', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('valpago', models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True)),
                ('valprincipal', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('valreajustes', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('valtotalempenhado', models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True)),
                ('data_extracao', models.DateField(blank=True, null=True)),
                ('dt_data_loaded', models.CharField(blank=True, max_length=26, null=True)),
            ],
            options={
                'db_table': 'contratos_raw_load',
            },
        ),
    ]