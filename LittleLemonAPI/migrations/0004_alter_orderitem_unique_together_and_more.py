# Generated by Django 5.0 on 2024-01-04 07:14

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("LittleLemonAPI", "0003_alter_orderitem_unique_together"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="orderitem",
            unique_together={("order", "menuitem")},
        ),
        migrations.RemoveField(
            model_name="orderitem",
            name="user",
        ),
    ]