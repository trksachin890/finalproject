# Generated by Django 4.2.7 on 2025-01-08 14:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_alter_orderitem_price_alter_orderitem_quantity_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='paid',
        ),
        migrations.RemoveField(
            model_name='order',
            name='payment_id',
        ),
    ]