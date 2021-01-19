import time
from app.BinanceAPI import BinanceAPI
from app.authorization import api_key, api_secret
from data.runBetData import RunBetData
from app.dingding import Message

api = BinanceAPI(api_key, api_secret)
runbet = RunBetData()
msg = Message()
class MainRun():
    def __init__(self):
        self.lastPrice = None # 上一个时间点的市场价格，为了计算一段时间的波动率
        self.symbol = runbet.get_symbol() # 运行的交易对
        self.waitTime = runbet.get_waitTime() #间隔时间
        self.expectVolare = runbet.get_expectVolare() #预期波动率
        self.openLeverageBase = runbet.get_openLeverageBase()  # 收益率大于基数才能开杠杆 
        self.amount = runbet.get_amount()      # 买入卖出数量
        self.maxLoass = runbet.get_maxLoss()   # 最大亏损比率
    
    def get_openPositionInfo(self):
        '''获取交易对持仓信息'''
        positionInfo = api.get_positionInfo(self.symbol)
        # print(positionInfo)
        if isinstance(positionInfo,list):
            return positionInfo[0]
        else:
            return None
        
    def closePositionDirection(self,positionAmt):
        '''执行平仓'''
        print("平仓")
        if float(positionAmt) < 0 : # 小于0代表做空，则做多卖出
            msg.buy_market_msg(self.symbol,self.amount) 
        else:
            msg.sell_market_msg(self.symbol,self.amount) 
    
    def judge_direction(self, positionAmt):
        '''
            判断多还是空
            @return boolean 做多为True 做空为False
        '''
        if float(positionAmt) > 0: #多
            return True
        else:
            return False
            
            
            
    # 主函数
    def run(self):
        
        info=self.get_openPositionInfo()
        # print(info)
        leverage = int(info['leverage'])
                    
        # 检测收益有无为负流程
        if info['notional'] != "0": # 已经开仓
            responseRate = round(float(info['unRealizedProfit']) / leverage / abs(float(info['notional'])),3)  # 盈利率
            # print(info)
            print("收益率:{rate}".format(rate=responseRate))
            if (leverage != 1 and responseRate <= 0.01) or (leverage == 1 and responseRate <= -self.maxLoass): # 满足则平仓
                self.closePositionDirection(info['positionAmt'])
                          
        # 波动率检测
        curPrice = api.get_ticker_price(self.symbol)
        if ins.lastPrice != None:    
            volare = round((curPrice - ins.lastPrice) / ins.lastPrice,3) # 波动率
            ins.lastPrice = curPrice
            print("波动率：{rate}".format(rate=volare))
            # 超过波动率
            if abs(volare) > self.expectVolare: 
                if volare > 0 : # 满足代表 波动率为+
                    if info['notional'] != "0": # 代表 已经开仓
                        if self.judge_direction(info['positionAmt']):
                            print("加杠杆！")
                            if leverage<10 :api.set_leverage(self.symbol,leverage+1)
                        else:             
                            print("减杠杆！")
                            if leverage>1 : api.set_leverage(self.symbol, leverage-1)                                            
                    else: # 未开仓,做多开仓
                        msg.buy_market_msg(self.symbol,self.amount)
                
                else: # 波动率为 负
                    if info['notional'] != "0": # 代表 已经开仓
                        if self.judge_direction(info['positionAmt']):
                            print("减杠杆！")
                            if leverage>1 : api.set_leverage(self.symbol,leverage-1)
                        else:             
                            print("加杠杆！")
                            if leverage<10: api.set_leverage(self.symbol, leverage+1)                                            
                    else: # 未开仓,做空开仓
                        msg.sell_market_msg(self.symbol,self.amount)                            

        else:            
            ins.lastPrice = curPrice # 刚启动上一份时间中市场价格为空  
            
        print("上个时间的价格{price}".format(price=ins.lastPrice))
        time.sleep(60 * ins.waitTime) # 价格间隔时间
        
if __name__ == "__main__":
    ins = MainRun()
    try:
        while True:
            ins.run()
    except BaseException as e:
        msg.dingding_warn("报警：交易对{symbol},停止运行".format(symbol=ins.symbol))
    # 调试阶段
    # while True:
    #     ins.run()