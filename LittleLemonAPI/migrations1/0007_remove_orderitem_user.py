# Generated by Django 5.0 on 2024-01-03 07:25

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("LittleLemonAPI", "0006_alter_order_user_alter_orderitem_user"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="orderitem",
            name="user",
        ),
    ]
