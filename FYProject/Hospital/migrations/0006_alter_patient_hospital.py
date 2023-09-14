# Generated by Django 3.2 on 2023-07-04 01:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Hospital', '0005_auto_20230704_0100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='hospital',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wagonjwa', to='Hospital.hospital'),
        ),
    ]