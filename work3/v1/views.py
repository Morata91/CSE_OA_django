from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Product, Sales
from .serializers import ProductSerializer, SalesSerializer
from rest_framework import status
from django.db.models import Sum
import math

# 在庫
class ProductView(APIView):
    
    #共通で使用する関数
    def get_object(self, name):
        print(f"商品名: '{name}'を検索します")
        try:
            product = Product.objects.get(name=name)
            print(f"商品名: {product.name} が見つかりました")
            return product
        except:
            print(f"商品名: '{name}' が見つかりませんでした")
            return None
    
    # (2)在庫チェック
    def get(self, request, name=None, format=None):
        print('(2)在庫チェック')
        if name:
            product = self.get_object(name)
            if product:
                res = {product.name: product.amount}
            else:
                res = {name: 0}
        else:
            # 全ての商品の在庫をチェック
            products = Product.objects.filter(amount__gt=0).order_by('name')
            res = {}
            res.update([(product.name, product.amount) for product in products])
        return Response(res, status.HTTP_200_OK)
    
    # (1)在庫の更新・作成
    def post(self, request, format=None):
        print('(1)更新or作成')
        product = self.get_object(request.data.get('name'))
        
        if product is not None:
            #既存の商品の数量を更新
            print('在庫を更新します（仕入）')
            res = request.data.copy()
            if 'amount' not in request.data:
                request.data['amount'] = 1
            request.data['amount'] += product.amount
            serializer = ProductSerializer(product, data=request.data)
            if serializer.is_valid() and request.data['amount'] > 0:
                serializer.save()
                res = Response(res, status.HTTP_200_OK)
                res.headers['Location'] = request.build_absolute_uri() + request.data.get('name')
                return res
            else:
                return Response({"message": "ERROR"}, status.HTTP_400_BAD_REQUEST)
        else:
            # 商品を作成
            print('新商品を作成します')
            res = request.data.copy()
            if 'amount' not in request.data:
                request.data['amount'] = 1
            serializer = ProductSerializer(data=request.data)
            if serializer.is_valid() and request.data['amount'] > 0:
                serializer.save()
                return Response(res, status.HTTP_201_CREATED)
            else:
                return Response({"message": "ERROR"}, status.HTTP_400_BAD_REQUEST)
    
    # (5)全削除
    def delete(self, request, format=None):
        Product.objects.all().delete()
        Sales.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# 売上
class SalesView(APIView):
    
    #共通で使用する関数
    def get_object(self, name):
        print(f"商品名: '{name}'を検索します")
        try:
            product = Product.objects.get(name=name)
            print(product.amount)
            print(f"商品名: {product.name} が見つかりました")
            return product
        except:
            print(f"商品名: '{name}' が見つかりませんでした")
            return None
    
    
    #(4)売上チェック
    def get(self, request, format=None):
        print("(4)売上チェック")
        total_earnings = Sales.objects.aggregate(total=Sum('earnings'))['total'] or 0
        
        total_earnings = math.ceil(total_earnings * 100) / 100
        return Response({"sales": total_earnings})
    
    
    # (3)販売
    def post(self, request, format=None):
        print('(3)販売')
        name = request.data.get('name')
        amount = request.data.get('amount', 1)
        
        if not name: # nameは必須
            return Response({"message": "ERROR"}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0: # 0以下はエラー
            return Response({"message": "ERROR"}, status=status.HTTP_400_BAD_REQUEST)

        if 'price' in request.data:
            if request.data['price'] <= 0: # 0以下の入力はエラー
                return Response({"message": "ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        price = request.data.get('price', 0)
            

        
        try:
            # 商品マスタが存在するか確認
            product = Product.objects.get(name=name)
        except:
            return Response({"message": "ERROR"}, status=status.HTTP_404_NOT_FOUND)

        # 在庫が足りるか確認
        if product.amount < amount: #足りなければエラー
            return Response({"message": "ERROR"}, status=status.HTTP_400_BAD_REQUEST)

        # 在庫数を減らす
        product.amount -= amount
        product.save()
        
        # 売上を登録
        sales_data = {
            "name": name,
            "quantity": amount,
            "price": price,
            "earnings": amount * price
        }
        serializer = SalesSerializer(data=sales_data)
        if serializer.is_valid():
            serializer.save()
            res = Response(request.data, status.HTTP_201_CREATED)
            res.headers['Location'] = f"{request.build_absolute_uri('/v1/sales/')}{name}"
            return res
        else:
            return Response({"message": "ERROR"}, status.HTTP_400_BAD_REQUEST)
        
        
    
