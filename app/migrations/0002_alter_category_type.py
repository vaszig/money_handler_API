# Generated by Django 3.2 on 2021-04-09 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='type',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]
