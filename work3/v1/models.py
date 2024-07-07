from django.db import models
from django.core.validators import RegexValidator

# Create your models here.


class Product(models.Model):
    """商品
    ・商品名は8文字以内でアルファベット大文字、小文字のみ（大文字小文字は区別）
    ・在庫数は0以上の整数
    """
    name = models.CharField(max_length=8, verbose_name='商品名', unique=True, validators=[RegexValidator(r'^[a-zA-Z]{1,8}$')], db_collation='utf8mb4_bin' )
    amount = models.IntegerField(verbose_name='在庫数')
    
class Sales(models.Model):
    name = models.CharField(max_length=8, verbose_name='商品名')
    quantity = models.IntegerField(verbose_name='数量')
    price = models.IntegerField(verbose_name='価格')