# Generated by Django 2.2.7 on 2019-12-04 07:47

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0002_accounttype_activation_secret'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AccountType',
            new_name='Profile',
        ),
    ]