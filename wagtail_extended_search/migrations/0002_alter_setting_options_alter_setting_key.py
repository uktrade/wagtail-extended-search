# Generated by Django 4.1.9 on 2023-07-18 10:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("wagtail_extended_search", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="setting",
            options={
                "permissions": (
                    ("view_explore", "View the global search explore page"),
                )
            },
        ),
        migrations.AlterField(
            model_name="setting",
            name="key",
            field=models.CharField(
                help_text="'Flat key' of the setting", max_length=200, unique=True
            ),
        ),
    ]