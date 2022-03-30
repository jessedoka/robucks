import requests as r
print('...Mining...')
while 1:
    r.get('http://127.0.0.1:5000/mine')
    amount = r.get('http://127.0.0.1:5000/amount').json()

    if amount['amount'] % 100 == 0:
        print(f'{amount["amount"]}th  has been reached')