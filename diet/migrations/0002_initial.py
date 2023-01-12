# Generated by Django 3.2.16 on 2023-01-12 09:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
        ('diet', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sidedata',
            name='user',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='user.info'),
        ),
        migrations.AddField(
            model_name='mainside',
            name='main',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='main', to='diet.data'),
        ),
        migrations.AddField(
            model_name='mainside',
            name='side',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='side', to='diet.sidedata'),
        ),
        migrations.AddField(
            model_name='filter',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='diet.filtercategory'),
        ),
        migrations.AddField(
            model_name='data',
            name='carbohydrate_type',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='data_carbohydrate_type', to='diet.filter'),
        ),
        migrations.AddField(
            model_name='data',
            name='flavor',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='data_flavor', to='diet.filter'),
        ),
        migrations.AddField(
            model_name='data',
            name='type',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='data_type', to='diet.filter'),
        ),
        migrations.AddField(
            model_name='data',
            name='user',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='user.info'),
        ),
    ]