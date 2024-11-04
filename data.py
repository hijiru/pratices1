import base64
import time
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from requests import get,post
from websocket import create_connection
import json
import hmac
import hashlib
import pandas as pd
KEY = 'WnerVewyf4o70etvdzFSJCIshdlNSNPuQBvjb3lWA7jVQlfJPoiuuMLbPPYP4slC'
SECERT = 'Dud7zQuOiOZboQTKEOAviWm9U2oh5claxG1yC1gsC1NWV0bP3DQsaahoaJUCnPxB'
def hmac_hashing(api_secret, payload):
         m = hmac.new(api_secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256)
         return m.hexdigest()
class binanace_account(object):
    def __init__(self, key=None, secret=None):
        self.key= key
        self.secret = secret
        
    # 设置请求参数：
    def ws_create_new_order(self,symbol,side,type,quantity):
        params = {
            'apiKey':        self.key,   
            'symbol':        symbol,
            'side':            side,
            'type':            type,
            'quantity':     quantity
        }
        # 参数中加时间戳：
        timestamp = int(time.time() * 1000) # 以毫秒为单位的 UNIX 时间戳
        params['timestamp'] = timestamp
        # 参数中加签名：
        payload = '&'.join([f'{param}={value}' for param, value in sorted(params.items())])
        signature = base64.b64encode(self.secret.sign(payload.encode('ASCII')))
        params['signature'] = signature.decode('ASCII')
        # 发送请求：
        request = { 
            'id': 'my_new_order',   
            'method': 'order.place',    
            'params': params
        }
        ws = create_connection('wss://ws-api.binance.com:9443/ws-api/v3')    
        ws.send(json.dumps(request))    
        result =  json.loads(ws.recv())
        ws.close()  
        return result
    
    def withdrawal(self,coin,withdrawOrderId,network,address,amount,walletType=''):
        url = 'https://api.binance.com/sapi/v1/capital/withdraw/apply'

        params ={
        'coin':coin,
        'withdrawOrderId':withdrawOrderId,
        'network':network,
        'walletType':walletType,
        'address': address,
        'amount': amount
        
        }
        timestamp = int(time.time() * 1000) # 以毫秒为单位的 UNIX 时间戳
        params['timestamp'] = timestamp

        payload = '&'.join([f'{param}={value}' for param, value in params.items()])
        signature = base64.b64encode(self.secret.sign(payload.encode('ASCII')))
        params['signature'] = signature

        headers = {
            'X-MBX-APIKEY': self.key
        }
        r=post(url,headers=headers,params=params)
        return r.json()

    def get_coin_info(self):
        url = 'https://api.binance.com/sapi/v1/capital/config/getall'

        params ={
        }
        timestamp = int(time.time() * 1000) # 以毫秒为单位的 UNIX 时间戳
        params['timestamp'] = timestamp
        
        payload = '&'.join([f'{param}={value}' for param, value in params.items()])
        #Ed25519
        # signature = base64.b64encode(self.secret.sign(payload.encode('ASCII')))
        #HMAC
        signature = hmac_hashing(SECERT, payload)
        params['signature'] = signature

        headers = {
            'X-MBX-APIKEY': self.key
        }
        r=get(url,headers=headers,params=params)
        return r.json()
    
    def get_balance(self,coin):
        url = 'https://api.binance.com/api/v3/account'
        params ={
        }
        timestamp = int(time.time() * 1000) # 以毫秒为单位的 UNIX 时间戳
        params['timestamp'] = timestamp

        payload = '&'.join([f'{param}={value}' for param, value in params.items()])
        signature = base64.b64encode(self.secret.sign(payload.encode('ASCII')))
        params['signature'] = signature

        headers = {
            'X-MBX-APIKEY': self.key
        }
        r=get(url,headers=headers,params=params)
        r1=r.json()
        if coin == 'usdt':
            return r1['balances'][11]['free']
        elif coin == 'btc':
             return r1['balances'][0]['free']
    def old_trades_lookup(self,Symbol,**kargs):
        url = 'https://fapi.binance.com/fapi/v1/historicalTrades'

        params ={
            'symbol':Symbol
        }
        params.update(kargs)
        timestamp = int(time.time() * 1000) # 以毫秒为单位的 UNIX 时间戳
        params['timestamp'] = timestamp
       
        payload = '&'.join([f'{param}={value}' for param, value in params.items()])
        #Ed25519
        # signature = base64.b64encode(self.secret.sign(payload.encode('ASCII')))
        #HMAC
        signature = hmac_hashing(SECERT, payload)
        params['signature'] = signature

        headers = {
            'X-MBX-APIKEY': self.key
        }
        # print(params)
        r=get(url,headers=headers,params=params)
        return r.json()


if __name__ == '__main__':
    clinet= binanace_account(KEY,SECERT)
    df=clinet.old_trades_lookup(Symbol='BTCUSDT',limit = 500)
    df=pd.DataFrame(df)
    # print(df)
    df.to_csv('data.csv', encoding='utf-8', index=False)
   
