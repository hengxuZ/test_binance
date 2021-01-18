# author-wechat：findpanpan

import requests, time, hmac, hashlib
# from app.authorization import recv_window,api_secret,api_key
from app.authorization import recv_window,api_secret,api_key

try:
    from urllib import urlencode
# python3
except ImportError:
    from urllib.parse import urlencode

class BinanceAPI(object):
    BASE_URL = "https://www.binance.com/api/v1"
    FUTURE_URL = "https://fapi.binance.com"
    BASE_URL_V3 = "https://api.binance.com/api/v3"
    PUBLIC_URL = "https://www.binance.com/exchange/public/product"

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret    
        
    ### --- 合约 --- ###
    def set_leverage(self,symbol, leverage):
        
        ''' 调整开仓杠杆
            :param symbol 交易对
            :param leverage 杠杆倍数
        '''
        path = "%s/fapi/v1/leverage" % self.FUTURE_URL
        params = {'symbol':symbol, 'leverage': leverage}
        return self._post(path, params)
    
    def get_positionInfo(self, symbol):
        '''当前持仓交易对信息'''
        path = "%s/fapi/v2/positionRisk" % self.FUTURE_URL
        params = {"symbol":symbol}
        time.sleep(1)
        return self._get(path, params)
    
    def future_market_order(self,side, market, quantity):
        
        ''' 合约市价单
            :param side: 做多or做空 BUY SELL
            :param market:币种类型。如：BTCUSDT、ETHUSDT
            :param quantity: 购买量
        '''
        path = "%s/fapi/v1/order" % self.FUTURE_URL
        params = self._order(market, quantity, side)
        return self._post(path, params)

    def get_ticker_price(self,market):
        '''获取交易对市场价格'''
        path = "%s/fapi/v1/ticker/price" % self.FUTURE_URL
        params = {"symbol":market}
        res =  self._get_no_sign(path,params)
        time.sleep(1)
        return float(res['price'])     

    def get_order(self,market,orderId):
        '''获取开仓订单信息'''
        path = "%s/fapi/v1/order" % self.FUTURE_URL
        params = {"symbol":market,"orderId":orderId}
        res = self._get(path, params)
        return res
    
    ### --- 私有函数  --- ###
    def _order(self, market, quantity, side, price=None):
        '''
        :param market:币种类型。如：BTCUSDT、ETHUSDT
        :param quantity: 购买量
        :param side: 订单方向，买还是卖
        :param price: 价格 默认市价单
        :return:
        '''
        params = {}

        if price is not None:
            params["type"] = "LIMIT"
            params["price"] = self._format(price)
            params["timeInForce"] = "GTC"
        else:
            params["type"] = "MARKET"

        params["symbol"] = market
        params["side"] = side
        params["quantity"] = '%.8f' % quantity

        return params
        
    def _get_no_sign(self, path, params={}):
        query = urlencode(params)
        url = "%s?%s" % (path, query)
        return requests.get(url, timeout=180, verify=True).json()    

    def _sign(self, params={}):
        data = params.copy()

        ts = int(1000 * time.time())
        data.update({"timestamp": ts})
        h = urlencode(data)
        b = bytearray()
        b.extend(self.secret.encode())
        signature = hmac.new(b, msg=h.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
        data.update({"signature": signature})
        return data
    
    def _get(self, path, params={}):
        params.update({"recvWindow": recv_window})
        query = urlencode(self._sign(params))
        url = "%s?%s" % (path, query)
        header = {"X-MBX-APIKEY": self.key}
        return requests.get(url, headers=header, \
            timeout=30, verify=True).json()
        
    def _post(self, path, params={}):
        params.update({"recvWindow": recv_window})
        query = self._sign(params)
        url = "%s" % (path)
        header = {"X-MBX-APIKEY": self.key}
        return requests.post(url, headers=header, data=query,timeout=180, verify=True).json()    

    def _format(self, price):
        return "{:.8f}".format(price)

if __name__ == "__main__":
    instance = BinanceAPI(api_key,api_secret)    
    # print(instance.set_leverage("EOSUSDT",5))
    print(instance.get_positionInfo("EOSUSDT"))
    # print(instance.get_orderInfo("EOSUSDT","9489137850"))
    # print(instance.future_market_order("BUY",'EOSUSDT',4))
       