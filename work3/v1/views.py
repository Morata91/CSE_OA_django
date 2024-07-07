from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import Product, Sales
from .serializers import ProductSerializer, SalesSerializer
from rest_framework import status
from django.db.models import F, Sum, Q
from collections import OrderedDict


# 在庫
class ProductView(APIView):
    
    #共通で使用する関数
    def get_object(self, name):
        print(f"商品名: '{name}'を検索します")
        try:
            product = Product.objects.get(Q(name=name))
            print(f"商品名: {product.name} が見つかりました")
            return product
        except Product.DoesNotExist:
            print(f"商品名: '{name}' が見つかりませんでした")
            return None
    
    # (2)在庫チェック
    def get(self, request, name=None, format=None):
        print('ge')
        if name:
            product = self.get_object(name)
            if product:
                res = {product.name: product.amount}
            else:
                res = {name: 0}
        else:
            # 全ての商品の在庫をチェック
            products = Product.objects.filter(amount__gt=0).order_by('name')
            res = OrderedDict((product.name, product.amount) for product in products)
        return Response(res, status.HTTP_200_OK)
    
    
    def post(self, request, format=None):
        product = self.get_object(request.data.get('name'))
        
        if product is not None:
            #既存の商品の数量を更新
            print('在庫を更新します（仕入）')
            print(type(request.build_absolute_uri()))
            if 'amount' not in request.data:
                request.data['amount'] = 1
            # if request.data['amount'] <= 0:
            request.data['amount'] += product.amount
            serializer = ProductSerializer(product, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            print('se:', f'{serializer.data}a')
            res = Response(serializer.data, status.HTTP_200_OK)
            res.headers['Location'] = request.build_absolute_uri() + request.data.get('name')
            return res
            # return Response(serializer.data, headers={'Location': })
        else:
            # 商品を作成
            print('新商品を作成します')
            serializer = ProductSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                print('se:', serializer)
                return Response(serializer.data, status.HTTP_201_CREATED)
            else:
                return Response({"message": "ERROR"}, status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, name, format=None):
        print('pu')
        product = self.get_object(name)
        serializer = ProductSerializer(instance=product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)
    
    
    # 在庫及び売上のデータを全て削除する
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
        except Product.DoesNotExist:
            print(f"商品名: '{name}' が見つかりませんでした")
            return None
    
    
    # 売上の合計を計算して返す
    def get(self, request, format=None):
        total_sales = Sales.objects.annotate(
            item_total=F('quantity') * F('price')
        ).aggregate(total=Sum('item_total'))['total'] or 0
        
        return Response({"sales": total_sales})
    
    
    def post(self, request, format=None):
        # 販売
        name = request.data.get('name')
        amount = request.data.get('amount', 1)
        price = request.data.get('price', 0)
        
        if not name:
            return Response({"message": "ERROR"}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({"message": "ERROR"}, status=status.HTTP_400_BAD_REQUEST)

        if price < 0:
            return Response({"message": "ERROR"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 商品マスタが存在するか確認
            product = Product.objects.get(name=name)
        except Product.DoesNotExist:
            return Response({"message": "ERROR"}, status=status.HTTP_404_NOT_FOUND)

        # 在庫が足りるか確認
        if product.amount < amount:
            return Response({"error": "Insufficient stock"}, status=status.HTTP_400_BAD_REQUEST)

        # 在庫数を減らす
        product.amount -= amount
        product.save()
        
        # 売上を登録
        sales_data = {
            "name": name,
            "quantity": amount,
            "price": price
        }
        serializer = SalesSerializer(data=sales_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        res = Response(request.data, status.HTTP_201_CREATED)
        res.headers['Location'] = f"{request.build_absolute_uri('/v1/sales/')}{name}"
        
        return res
    
