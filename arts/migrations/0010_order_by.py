# Generated by Django 2.2.7 on 2019-12-10 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('arts', '0009_product_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='by',
            field=models.CharField(choices=[('O', 'On Site'), ('L', 'By Email Link')], default='O', max_length=1),
        ),
    ]
