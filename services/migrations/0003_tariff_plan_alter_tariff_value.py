# Generated by Django 4.2.2 on 2023-06-30 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("services", "0002_tariff_remove_recharge_created_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="tariff",
            name="plan",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name="tariff",
            name="value",
            field=models.IntegerField(),
        ),
    ]