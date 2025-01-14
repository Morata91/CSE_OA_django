# Generated by Django 5.0.6 on 2024-07-07 09:54

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('v1', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(db_collation='utf8mb4_bin', max_length=8, unique=True, validators=[django.core.validators.RegexValidator('^[a-zA-Z]{1,8}$')], verbose_name='商品名'),
        ),
    ]
