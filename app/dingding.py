# author-wechat：findpanpan

import requests,json,time

from app.BinanceAPI import BinanceAPI
from app.authorization import recv_window,api_secret,api_key, dingding_token


class Message():

    def __init__(self):
        self.api = BinanceAPI(api_key,api_secret)
        

    def buy_market_msg(self,market,quantity):
        '''
            买入带有钉钉消息的封装
            :param market:
            :param quantity: 数量
            :param rate: 价格
            :return:
        '''        
        
        try:
            self.api.set_leverage(market,1) # 无论买还是卖都要把杠杆设置为1

            res = self.api.future_market_order("BUY",market,quantity)
            print(res)
            if res['orderId']:
                buy_info = "报警：趋势交易，币种为：{cointype}。".format(cointype=market)
                self.dingding_warn(buy_info)
                return res                        
        except BaseException as e:
            error_info = "报警：币种为：{cointype},买单失败.api返回内容为:{reject}".format(cointype=market,reject=res['msg'])
            self.dingding_warn(error_info)

    def sell_market_msg(self,market,quantity):
        '''
            卖出带有钉钉消息的封装
            :param market:
            :param quantity: 数量
            :param rate: 价格
            :return:
        '''        
        
        try:
            self.api.set_leverage(market,1) # 无论买还是卖都要把杠杆设置为1
            res = self.api.future_market_order("SELL",market,quantity)
            if res['orderId']:
                buy_info = "报警：趋势交易，币种为：{cointype}。".format(cointype=market)
                self.dingding_warn(buy_info)
                return res                        
        except BaseException as e:
            error_info = "报警：币种为：{cointype},卖单失败.api返回内容为:{reject}".format(cointype=market,reject=res['msg'])
            self.dingding_warn(error_info)  

    def dingding_warn(self,text):
        headers = {'Content-Type': 'application/json;charset=utf-8'}
        api_url = "https://oapi.dingtalk.com/robot/send?access_token=%s" % dingding_token
        json_text = self._msg(text)
        requests.post(api_url, json.dumps(json_text), headers=headers).content

    def _msg(self,text):
        json_text = {
            "msgtype": "text",
            "at": {
                "atMobiles": [
                    "11111"
                ],
                "isAtAll": False
            },
            "text": {
                "content": text
            }
        }
        return json_text
            
if __name__ == "__main__":
    mes = Message()
    print(mes.buy_market_msg("EOSUSDT",2))
    pass