# Generated by Django 3.2 on 2023-06-22 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Hospital', '0002_auto_20230622_1923'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hospital',
            name='coords',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='hospital',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='hospital',
            name='physical_address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
