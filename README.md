



### 3. 販売
```bash
curl -v -d '{"name": "yyy"}' -H 'Content-Type: application/json' http://127.0.0.1:8000/v1/sales/
```
```bash
curl -v -d '{"name": "aaa", "amount": 4}' -H 'Content-Type: application/json' http://127.0.0.1:8000/v1/sales
```
```bash
curl -v -d '{"name": "aaa", "amount": 4, "price": 100}' -H 'Content-Type: application/json' http://127.0.0.1:8000/v1/sales
```


### 4. 売上チェック
```bash
curl  http://127.0.0.1:8000/v1/sales/
```


### 5. 全削除
```bash
curl -X DELETE http://127.0.0.1:8000/v1/stocks
```


### 実行例1
```bash
curl -X DELETE http://127.0.0.1:8000/v1/stocks

curl -d '{"name": "xxx", "amount": 100}' -H 'Content-Type: application/json' http://127.0.0.1:8000/v1/stocks
# {"name":"xxx","amount":100}

curl -d '{"name": "xxx", "amount": 4}' -H 'Content-Type: application/json' http://127.0.0.1:8000/v1/sales
# {"name":"xxx","amount":4}

curl http://127.0.0.1:8000/v1/stocks
# {"xxx":96}

curl -d '{"name": "yyy", "amount": 100}' -H 'Content-Type: application/json' http://127.0.0.1:8000/v1/stocks
# {"name":"yyy","amount":100}

curl -d '{"name": "YYY", "amount": 100}' -H 'Content-Type: application/json' http://127.0.0.1:8000/v1/stocks
# {"name":"YYY","amount":100}

curl http://127.0.0.1:8000/v1/stocks
# {"YYY":100,"xxx":96,"yyy":100}
```

### 実行例2
```bash
curl -X DELETE http://127.0.0.1:8000/v1/stocks

curl -d '{"name": "xxx", "amount": 1.1}' -H 'Content-Type: application/json' http://127.0.0.1:8000/v1/stocks
# {"message":"ERROR"}
```



### 実行例3
```bash
curl -X DELETE http://127.0.0.1:8000/v1/stocks

curl -d '{"name": "aaa", "amount": 10}' -H 'Content-Type: application/json' http://127.0.0.1:8000/v1/stocks
# {"name":"aaa","amount":10}

curl -d '{"name": "bbb", "amount": 10}' -H 'Content-Type: application/json' http://127.0.0.1:8000/v1/stocks
# {"name":"bbb","amount":10}

curl -d '{"name": "aaa", "amount": 4, "price": 100}' -H 'Content-Type: application/json' http://127.0.0.1:8000/v1/sales
# {"name":"aaa","amount":4,"price":100}

curl -d '{"name": "aaa", "price": 80}' -H 'Content-Type: application/json' http://127.0.0.1:8000/v1/sales
# {"name":"aaa","price":80}

curl http://127.0.0.1:8000/v1/sales
# {"sales":480.0}
```




sudo tail -n 50 /var/log/httpd/error_log