# Generated by Django 5.0.4 on 2024-05-26 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Table1',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('CropType', models.CharField(max_length=1000)),
                ('SoilMoistureValue', models.PositiveIntegerField()),
                ('ET0', models.DecimalField(decimal_places=2, max_digits=10)),
                ('ETc', models.DecimalField(decimal_places=2, max_digits=10)),
                ('IRn', models.DecimalField(decimal_places=2, max_digits=10)),
                ('IR', models.DecimalField(decimal_places=2, max_digits=10)),
                ('Dw', models.DecimalField(decimal_places=2, max_digits=10)),
                ('IDG', models.DecimalField(decimal_places=2, max_digits=10)),
                ('Wf', models.PositiveIntegerField()),
                ('city', models.CharField(max_length=1000)),
                ('Date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Table2',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('CropType', models.CharField(max_length=1000)),
                ('SoilMoistureValue', models.PositiveIntegerField()),
                ('ET0', models.DecimalField(decimal_places=2, max_digits=10)),
                ('ETc', models.DecimalField(decimal_places=2, max_digits=10)),
                ('IRn', models.DecimalField(decimal_places=2, max_digits=10)),
                ('IR', models.DecimalField(decimal_places=2, max_digits=10)),
                ('Dw', models.DecimalField(decimal_places=2, max_digits=10)),
                ('IDG', models.DecimalField(decimal_places=2, max_digits=10)),
                ('Wf', models.PositiveIntegerField()),
                ('city', models.CharField(max_length=1000)),
                ('Date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
