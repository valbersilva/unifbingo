# Generated by Django 5.2 on 2025-04-14 00:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auditlog'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='nickname',
            new_name='username',
        ),
    ]
