# Generated by Django 4.2.7 on 2024-12-31 15:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_rename_contactus_contact_us_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Categories',
            new_name='Category',
        ),
    ]