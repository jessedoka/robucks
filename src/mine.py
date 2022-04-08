import requests as r
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
args = parser.parse_args()   
port = args.port

host = 'http://localhost:' + str(port)

print('...Mining...')
while 1:
    r.get(f'{host}/mine')
    amount = r.get(f'{host}/amount').json()

    if amount['amount'] % 100 == 0:
        print(f'{amount["amount"]}th  has been reached')