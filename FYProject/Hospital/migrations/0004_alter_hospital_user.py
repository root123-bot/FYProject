# Generated by Django 3.2 on 2023-06-22 23:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Hospital', '0003_auto_20230622_1931'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hospital',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='hospital', to=settings.AUTH_USER_MODEL),
        ),
    ]
