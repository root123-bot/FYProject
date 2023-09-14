# Generated by Django 3.2 on 2023-09-14 04:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Hospital', '0013_alter_patient_department'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='doctors', to='Hospital.department'),
        ),
    ]