# Generated by Django 5.2.1 on 2025-05-27 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_alter_land_land_surface'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apartment',
            name='rooms',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='apartment',
            name='surface',
            field=models.DecimalField(decimal_places=1, max_digits=10),
        ),
        migrations.AlterField(
            model_name='commercialspace',
            name='surface',
            field=models.DecimalField(decimal_places=1, max_digits=10),
        ),
        migrations.AlterField(
            model_name='house',
            name='land_surface',
            field=models.DecimalField(decimal_places=1, max_digits=10),
        ),
        migrations.AlterField(
            model_name='house',
            name='rooms',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='house',
            name='surface',
            field=models.DecimalField(decimal_places=1, max_digits=10),
        ),
        migrations.AlterField(
            model_name='land',
            name='land_surface',
            field=models.DecimalField(decimal_places=1, max_digits=10),
        ),
    ]
