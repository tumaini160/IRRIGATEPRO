# Generated by Django 5.0.4 on 2024-04-19 04:25

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Results',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ET0', models.DecimalField(decimal_places=2, max_digits=10)),
                ('ETc', models.DecimalField(decimal_places=2, max_digits=10)),
                ('IRn', models.DecimalField(decimal_places=2, max_digits=10)),
                ('IR', models.DecimalField(decimal_places=2, max_digits=10)),
                ('Dw', models.DecimalField(decimal_places=2, max_digits=10)),
                ('IDG', models.DecimalField(decimal_places=2, max_digits=10)),
                ('Wf', models.PositiveIntegerField()),
                ('city', models.CharField(max_length=1000)),
                ('Date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='SensorData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('SoilMoistureValue', models.PositiveIntegerField()),
                ('Date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
