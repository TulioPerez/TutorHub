# Generated by Django 5.1.4 on 2025-01-06 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tutorhub", "0004_user_middle_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="middle_name",
            field=models.CharField(blank=True, default="", max_length=50, null=True),
        ),
    ]
