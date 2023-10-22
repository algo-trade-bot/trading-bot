import requests
import urllib.parse
import hashlib
import hmac
import base64
import os
import time
from dotenv import load_dotenv, find_dotenv


class TradeController():

    load_dotenv(find_dotenv())
    api_key = os.environ.get("API_KEY")
    api_sec = os.environ.get("API_SECRET")

    def __init__(self, api_key=api_key) -> None:
        self.headers = {
        'API-Key': api_key
        }


    def generate_nonce(self):
        return int(time.time())


    def get_kraken_signature(self, uripath, data, secret=api_sec):
        postdata = urllib.parse.urlencode(data)
        encoded = (str(data['nonce']) + postdata).encode()
        message = uripath.encode() + hashlib.sha256(encoded).digest()

        mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
        sigdigest = base64.b64encode(mac.digest())
        self.headers['API-Sign'] = sigdigest.decode()


    def get_asset_info(self, asset_name, url="https://api.kraken.com/0/public/Assets"):
        post_data = {
            'asset': asset_name
        }

        return requests.post(url=url, data=post_data).json()
    
    
    def get_deposit_methods(self, asset_name, url="https://api.kraken.com/0/private/DepositMethods", uri='/0/private/DepositMethods'):
        post_data = {
            'nonce': self.generate_nonce(),
            'asset': asset_name
        }
        print(post_data)
        self.get_kraken_signature(uri, data=post_data)

        return requests.post(url, headers=self.headers, data=post_data).json()
        


if __name__ == '__main__':
    trade = TradeController()
    btc_info = trade.get_deposit_methods('BTC')
    print(btc_info)