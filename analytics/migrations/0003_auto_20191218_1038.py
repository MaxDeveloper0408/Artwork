# Generated by Django 2.2.7 on 2019-12-18 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0002_auto_20191218_1006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goal',
            name='target_time',
            field=models.CharField(choices=[('M', 'Monthly'), ('W', 'Weekly'), ('Y', 'Yearly')], max_length=1),
        ),
    ]
