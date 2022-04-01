import requests as r
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
args = parser.parse_args()   
port = args.port

print('...Mining...')
while 1:
    r.get(f'http://127.0.0.1:{port}/mine')
    amount = r.get(f'http://127.0.0.1:{port}/amount').json()

    if amount['amount'] % 100 == 0:
        print(f'{amount["amount"]}th  has been reached')