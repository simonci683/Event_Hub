# Generated by Django 5.2.1 on 2025-05-28 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Event_Hub', '0002_carrello'),
    ]

    operations = [
        migrations.AddField(
            model_name='evento',
            name='prezzo',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
