# Generated by Django 5.0.6 on 2024-07-07 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('v1', '0002_alter_product_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='sales',
            name='earnings',
            field=models.FloatField(default=0, verbose_name='売上'),
        ),
        migrations.AlterField(
            model_name='sales',
            name='price',
            field=models.FloatField(verbose_name='価格'),
        ),
    ]
