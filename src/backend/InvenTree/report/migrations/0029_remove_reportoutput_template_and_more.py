# Generated by Django 4.2.19 on 2025-03-07 01:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("report", "0028_labeltemplate_attach_to_model_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="reportoutput",
            name="template",
        ),
        migrations.RemoveField(
            model_name="reportoutput",
            name="user",
        ),
        migrations.DeleteModel(
            name="LabelOutput",
        ),
        migrations.DeleteModel(
            name="ReportOutput",
        ),
    ]
