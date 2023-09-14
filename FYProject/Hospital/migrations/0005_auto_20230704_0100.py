# Generated by Django 3.2 on 2023-07-04 01:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Hospital', '0004_alter_hospital_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='hospital',
            name='no_of_doctors',
            field=models.CharField(default='0', max_length=200),
        ),
        migrations.AddField(
            model_name='patient',
            name='assigned_to',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='patient',
            name='is_using_NHIF',
            field=models.BooleanField(default=False),
        ),
    ]
