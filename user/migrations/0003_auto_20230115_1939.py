# Generated by Django 3.2.16 on 2023-01-15 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_alter_info_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='info',
            name='activity',
            field=models.IntegerField(choices=[(-1, 'Nochoices'), (0, 'Deeplow'), (1, 'Low'), (2, 'Middle'), (3, 'High'), (4, 'Deephigh')], default=-1, null=True),
        ),
        migrations.AlterField(
            model_name='info',
            name='gender',
            field=models.CharField(choices=[('', 'Nochoices'), ('f', 'Female'), ('m', 'Male')], default='', max_length=1, null=True),
        ),
    ]
