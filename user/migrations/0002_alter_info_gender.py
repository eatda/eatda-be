# Generated by Django 3.2.16 on 2023-01-15 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='info',
            name='gender',
            field=models.CharField(choices=[('', 'Nochoices'), ('f', 'Female'), ('m', 'Male')], default='', max_length=1),
        ),
    ]