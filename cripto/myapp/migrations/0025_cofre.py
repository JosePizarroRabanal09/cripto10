# Generated by Django 4.2.5 on 2024-03-31 04:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0024_userinfo_gold_total'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cofre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('imagen', models.ImageField(upload_to='')),
                ('sonido', models.FileField(upload_to='')),
            ],
        ),
    ]
