# Generated by Django 2.2.3 on 2019-07-22 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contratos', '0004_auto_20190717_2108'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmpenhoSOFFailedAPIRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cod_contrato', models.IntegerField()),
                ('ano_exercicio', models.IntegerField()),
                ('ano_empenho', models.IntegerField()),
                ('error_code', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]