# Generated by Django 5.2 on 2025-06-21 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_alter_servicesession_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicesession',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='Phone Number'),
        ),
    ]
