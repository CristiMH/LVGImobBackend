# Generated by Django 5.2.1 on 2025-05-27 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_alter_listing_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='land',
            name='land_surface',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
