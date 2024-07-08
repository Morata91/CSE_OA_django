# 課題1
WebサーバーにはApacheを使用
### 参考にしたもの
- 7/4実施 オンラインアセスメント対策講座
## Apacheのインストール
```bash
# yumのアップデート
sudo yum update -y

# Apacheのインストール
sudo yum install -y httpd httpd-devel
httpd -v
# Server version: Apache/2.4.59 ()

# Apacheの起動
sudo systemctl start httpd

# Apacheの状態確認
sudo systemctl status httpd

# 自動起動設定
sudo systemctl enable httpd

# Apache自動起動設定の確認
sudo systemctl is-enabled httpd
# enabled
```
## index.htmlを作成
```html
# /var/www/html/index.html
AWS
```
## 確認
```bash
curl http://54.64.143.21/
# AWS
```

---

# 課題2
### Basic認証との共通点
ID、パスワードによる認証
### Basic認証との相違点
パスワードをハッシュ化して送信→盗聴されても簡単にはパスワードがバレない
### 参考にしたもの
- https://www.javadrive.jp/apache/allow/index8.html
- https://qiita.com/gama1234/items/bfda469f525811a3aa79
## secret/index.htmlを作成
```
# /var/www/html/secret/index.html
SUCCESS
```

## ダイジェスト認証用のユーザー情報を作成し保存
```bash
sudo htdigest -c /etc/httpd/.htdigest "Secret Page" aws
```
## ディレクトリの設定
```
# /etc/httpd/conf/httpd.conf
<Directory "/var/www/html/secret">
    AuthType Digest
    AuthName "Secret Page"
    AuthUserFile "/etc/httpd/.htdigest"
    Require valid-user
</Directory>
```
## 確認
```bash
# Apacheの再起動
sudo systemctl restart httpd

curl http://54.64.143.21/secret
# <!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
# <html><head>
# <title>401 Unauthorized</title>
# </head><body>
# <h1>Unauthorized</h1>
# <p>This server could not verify that you
# are authorized to access the document
# requested.  Either you supplied the wrong
# credentials (e.g., bad password), or your
# browser doesn't understand how to supply
# the credentials required.</p>
# </body></html>

curl -L --digest -u aws:candidate http://xx.xx.xx.xx/secret
# SUCCESS
```



# 課題3
Django+MySQL(+mod_wsgi)で、商品在庫管理APIの実装
### 要件
- 予期しない入力に対しては、全て{"message": "ERROR"} を返す。
- 商品名は8文字以内、アルファベットの大文字・小文字
### システム構造と選んだ理由
- Webアプリケーションフレームワーク：Django
研究等でPythonを使うことが多いため。 REST APIを作成するフレームワークがあり便利。
- DBMS：MySQL
人気があり、文献が豊富。速い。


### 参考にしたもの
- https://hirahira.blog/ec2deploy-django/
- https://youtu.be/cuZuxvulGF4?si=jT1KvaKLF5heYLqp
- その他（Webサーバー、wsgi、DBの基本をwebサイトやYouTubeでキャッチアップ）

## ローカルの開発環境でDjango+MySQLによるAPIの実装
ソースコードにて

## EC2サーバー上にデプロイ
### MySQLのインストール
```bash
sudo yum remove -y mariadb-*
sudo yum localinstall -y https://dev.mysql.com/get/mysql80-community-release-el7-11.noarch.rpm
sudo yum install -y --enablerepo=mysql80-community mysql-community-server

#DjangoからMySQLを操作するためのドライバ
sudo yum install -y mysql-community-devel

mysql --version
# mysql  Ver 8.0.38 for Linux on x86_64 (MySQL Communaaaity Server - GPL)
```

### 必要なものをインストール
```bash
sudo yum install -y python3-devel gcc gcc-c++
sudo yum install -y git
```

### Djangoプロジェクトをクローン
Githubプライベートリポジトリ経由で、EC2上に持ってきた
```bash
cd /var/www/
git clone https://github.com/Morata91/CSE_OA_django.git
```

### 仮想環境上にDjangoなどをインストール
```bash
cd CSE_OA_django/
python3 -m venv .env
source .env/bin/activate
pip3 install -r requirements.txt
```
```
# requirements.txt
Django
mysqlclient
djangorestframework
mod_wsgi
```

### MySQLの設定
```bash
#　MySQLの起動
sudo systemctl start mysqld.service

#　起動確認
sudo systemctl status mysqld.service

#　サーバー起動時にMySQLを自動起動するよう設定
sudo systemctl enable mysqld.service

# 初期パスワードを確認
sudo cat /var/log/mysqld.log

# MySQLへ接続する（上記で設定したパスワードを入力する）
mysql -u root -p

# パスワード設定
mysql> ALTER USER 'root'@'localhost' identified BY 'kjn3Ak*kWe24';

#データベース作成
mysql> create database cse_oa_db;

#　MySQL切断
mysql> exit
```

### Djangoプロジェクトの設定
#### setting.pyを編集
```python
# /var/www/CSE_OA_django/work3/work3/settings.py
import os # 追加

ALLOWED_HOSTS = ['54.64.143.21'] # 編集

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cse_oa_db',
        'USER': 'root',
        'PASSWORD': 'kjn3Ak*kWe24', # 編集
        'PORT': '3306',
        'ATOMIC_REQUESTS': True,
        'OPTIONS': {
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_bin',  # 大文字小文字を区別する照合順序
        },
    }
}
```
#### マイグレーション
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### WSGIの設定
####　/etc/httpd/conf.d/配下にDjangoプロジェクトの設定ファイルを作成
```
# /etc/httpd/conf.d/myproject.conf

LoadModule wsgi_module /var/www/CSE_OA_django/.env/lib/python3.7/site-packages/mod_wsgi/server/mod_wsgi-py37.cpython-37m-x86_64-linux-gnu.so


ServerName <54.64.143.21>

WSGIDaemonProcess myproject python-home=/var/www/CSE_OA_django/.env python-path=/var/www/CSE_OA_django/work3
WSGIProcessGroup myproject
WSGIScriptAlias /v1 /var/www/CSE_OA_django/work3/work3/wsgi.py process-group=myproject

<Directory /var/www/CSE_OA_django/work3/work3>
<Files wsgi.py>
Require all granted
</Files>
</Directory>
```

### 確認
Apacheを再起動した後、実行例を試した。




# 課題3 プログラムコード抜粋 (必須):
## モデルの定義
### 参考にしたもの
- 佐藤大輔「実装で学ぶ　フルスタックWeb開発」
```python
# v1/models.py
class Product(models.Model):
    # 商品名は8文字以内でアルファベット大文字、小文字のみ（大文字小文字は区別）
    name = models.CharField(max_length=8, verbose_name='商品名', unique=True, validators=[RegexValidator(r'^[a-zA-Z]{1,8}$')], db_collation='utf8mb4_bin' )
    amount = models.IntegerField(verbose_name='在庫数')
    
class Sales(models.Model):
    name = models.CharField(max_length=8, verbose_name='商品名')
    quantity = models.IntegerField(verbose_name='数量')
    price = models.FloatField(verbose_name='価格')
    earnings = models.FloatField(verbose_name='売上=数量*価格', default=0)
```

## 各APIの作成
Django REST Frameworkを使用した。
### 参考にしたもの
- 佐藤大輔「実装で学ぶ　フルスタックWeb開発」
```python
# views.py

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
```

## シリアライザーの作成
Django REST Frameworkのserializersを使用し、オブジェクトをjson形式に変換
### 参考にしたもの
- 佐藤大輔「実装で学ぶ　フルスタックWeb開発」
```python
# v1/serializers.py
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        # fields = '__all__'
        fields = ['name', 'amount']
    
class SalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sales
        fields = '__all__'
```


