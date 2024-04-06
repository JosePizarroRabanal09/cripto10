# Generated by Django 4.2.5 on 2024-03-24 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0009_compra_hora_habilitacion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guerrero',
            name='precio',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='withdraw',
            name='status',
            field=models.CharField(choices=[('P', 'Pending'), ('A', 'Approved'), ('R', 'Refused')], default='P', max_length=1),
        ),
    ]
