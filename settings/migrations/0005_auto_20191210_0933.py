# Generated by Django 2.2.7 on 2019-12-10 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0004_menu_usermenu'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usermenu',
            name='role',
        ),
        migrations.AddField(
            model_name='usermenu',
            name='for_admin',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='usermenu',
            name='for_artist',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='usermenu',
            name='for_collector',
            field=models.BooleanField(default=False),
        ),
    ]
