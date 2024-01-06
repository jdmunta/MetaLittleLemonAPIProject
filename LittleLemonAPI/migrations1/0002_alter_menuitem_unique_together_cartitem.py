# Generated by Django 5.0 on 2023-12-09 04:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("LittleLemonAPI", "0001_initial"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="menuitem",
            unique_together={("title", "category")},
        ),
        migrations.CreateModel(
            name="CartItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.PositiveIntegerField(default=1)),
                (
                    "cart",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="LittleLemonAPI.cart",
                    ),
                ),
                (
                    "menuitem",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="LittleLemonAPI.menuitem",
                    ),
                ),
            ],
        ),
    ]