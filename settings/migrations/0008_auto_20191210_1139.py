# Generated by Django 2.2.7 on 2019-12-10 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0007_auto_20191210_0934'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usermenu',
            options={'ordering': ['menu']},
        ),
        migrations.AddField(
            model_name='menu',
            name='link',
            field=models.TextField(blank=True, null=True),
        ),
    ]
