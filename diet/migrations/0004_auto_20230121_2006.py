# Generated by Django 3.2.16 on 2023-01-21 20:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('diet', '0003_auto_20230117_1805'),
    ]

    operations = [
        migrations.AddField(
            model_name='data',
            name='side',
            field=models.ManyToManyField(related_name='main', through='diet.MainSide', to='diet.SideData'),
        ),
        migrations.AlterField(
            model_name='data',
            name='ingredient',
            field=models.TextField(default='[]'),
        ),
        migrations.AlterField(
            model_name='mainside',
            name='main',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='main_side', to='diet.data'),
        ),
        migrations.AlterField(
            model_name='mainside',
            name='side',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='main_side', to='diet.sidedata'),
        ),
        migrations.AlterField(
            model_name='sidedata',
            name='ingredient',
            field=models.TextField(default='[]'),
        ),
    ]
