# Generated by Django 5.1.4 on 2025-01-06 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tutorhub", "0002_user_allow_spotlight_user_show_birthdate_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="missing_profile_data_alert",
            field=models.BooleanField(default=False),
        ),
    ]