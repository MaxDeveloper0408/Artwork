# Generated by Django 2.2.7 on 2019-12-06 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('arts', '0004_auto_20191205_1117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='price',
            field=models.IntegerField(),
        ),
    ]