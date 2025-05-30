# Generated by Django 5.2.1 on 2025-05-11 12:47

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_remove_listing_unique_listing_type_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sector',
            options={'ordering': ['sector']},
        ),
        migrations.AlterField(
            model_name='apartment',
            name='condition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='apartments', to='api.condition'),
        ),
        migrations.AlterField(
            model_name='apartment',
            name='construction_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='apartments', to='api.constructiontype'),
        ),
        migrations.AlterField(
            model_name='apartment',
            name='heating_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='apartments', to='api.heatingtype'),
        ),
        migrations.AlterField(
            model_name='apartment',
            name='listing',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='apartment', to='api.listing'),
        ),
        migrations.AlterField(
            model_name='apartment',
            name='planning_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='apartments', to='api.planningtype'),
        ),
        migrations.AlterField(
            model_name='commercialspace',
            name='condition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commercial_spaces', to='api.condition'),
        ),
        migrations.AlterField(
            model_name='commercialspace',
            name='listing',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='commercial_space', to='api.listing'),
        ),
        migrations.AlterField(
            model_name='house',
            name='listing',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='house', to='api.listing'),
        ),
        migrations.AlterField(
            model_name='land',
            name='listing',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='land', to='api.listing'),
        ),
        migrations.AlterField(
            model_name='land',
            name='surface_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lands', to='api.surfacetype'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='listing',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listings', to='api.location'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='modified_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='listing',
            name='price',
            field=models.DecimalField(db_index=True, decimal_places=2, max_digits=12),
        ),
        migrations.AlterField(
            model_name='listing',
            name='property_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listings', to='api.propertytype'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='sale_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listings', to='api.saletype'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='sector',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='listings', to='api.sector'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listings', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='message',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='phone',
            field=models.CharField(max_length=15, validators=[django.core.validators.RegexValidator(message='Numărul de telefon nu este valid. Ex: +37369123456', regex='^\\+?[\\d\\s()-]{7,15}$')]),
        ),
        migrations.AlterField(
            model_name='request',
            name='condition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='api.condition'),
        ),
        migrations.AlterField(
            model_name='request',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='request',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='api.location'),
        ),
        migrations.AlterField(
            model_name='request',
            name='phone',
            field=models.CharField(max_length=15, validators=[django.core.validators.RegexValidator(message='Numărul de telefon nu este valid. Ex: +37369123456', regex='^\\+?[\\d\\s()-]{7,15}$')]),
        ),
        migrations.AlterField(
            model_name='request',
            name='property_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='api.propertytype'),
        ),
        migrations.AlterField(
            model_name='request',
            name='sector',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='api.sector'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='modified_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(max_length=15, validators=[django.core.validators.RegexValidator(message='Numărul de telefon nu este valid. Ex: +37369123456', regex='^\\+?[\\d\\s()-]{7,15}$')]),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users', to='api.usertype'),
        ),
    ]
