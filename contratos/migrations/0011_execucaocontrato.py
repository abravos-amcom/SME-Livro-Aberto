# Generated by Django 2.2.3 on 2019-08-03 22:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contratos', '0010_contratomodalidade_fornecedor_objetocontrato'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExecucaoContrato',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cod_contrato', models.IntegerField()),
                ('empenho_indexer', models.CharField(max_length=28)),
                ('year', models.DateField()),
                ('valor_empenhado', models.FloatField()),
                ('valor_liquidado', models.FloatField()),
                ('categoria', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='contratos.ContratoCategoria')),
                ('fornecedor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contratos.Fornecedor')),
                ('modalidade', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contratos.ContratoModalidade')),
                ('objeto_contrato', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contratos.ObjetoContrato')),
            ],
        ),
    ]
