# Generated by Django 4.2.22 on 2025-06-09 02:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("plugin", "0009_alter_pluginconfig_key"),
    ]

    operations = [
        migrations.CreateModel(
            name="PluginUserSetting",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("key", models.CharField(help_text="Settings key", max_length=50)),
                (
                    "value",
                    models.CharField(
                        blank=True, help_text="Settings value", max_length=2000
                    ),
                ),
                (
                    "plugin",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_settings",
                        to="plugin.pluginconfig",
                        verbose_name="Plugin",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        help_text="User",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="plugin_settings",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "unique_together": {("plugin", "user", "key")},
            },
        ),
    ]
