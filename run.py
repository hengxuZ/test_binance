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
        self.smallProfit = runbet.get_smallProfit()  # 收益率大于基数才能加仓 
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
        
    def closePositionDirection(self,positionAmt,curPrice):
        '''执行平仓'''
        print("平仓")
        total = abs(float(positionAmt))
        if float(positionAmt) < 0 : # 小于0代表做空，则做多卖出
            msg.buy_limit_msg(self.symbol,total,curPrice) 
        else:
            msg.sell_limit_msg(self.symbol,total,curPrice) 
    
    def judge_direction(self, positionAmt):
        '''
            判断多还是空
            @return boolean 做多为True 做空为False
        '''
        if float(positionAmt) > 0: #多
            return True
        else:
            return False
        
    def judge_is_firstPosition(self, positionNum):
        '''
            positionNum : 当前持仓量
            判断持仓量是否为第一次买入or卖出
            @return blllean 
        '''   
                 
        flag = True if abs(float(positionNum)) == self.amount else False
        return flag
            
            
    # 主函数
    def run(self):
        
        info=self.get_openPositionInfo()
        # print(info)
        leverage = int(info['leverage'])  
        curPrice = api.get_ticker_price(self.symbol) #获取当前价格        
        # 检测收益有无为负流程
        if info['notional'] != "0": # 已经开仓
            responseRate = round(float(info['unRealizedProfit']) / leverage / abs(float(info['notional'])),3)  # 盈利率
            # print(info)
            print("收益率:{rate}".format(rate=responseRate))
            if (self.judge_is_firstPosition(info["positionAmt"]) and responseRate <= -self.maxLoass) or (not self.judge_is_firstPosition(info["positionAmt"]) and responseRate <= 0): # 满足则平仓
                self.closePositionDirection(info['positionAmt'],curPrice)
                          
        # 波动率检测
        if ins.lastPrice != None:    
            volare = round((curPrice - ins.lastPrice) / ins.lastPrice,3) # 波动率
            ins.lastPrice = curPrice
            print("波动率：{rate}".format(rate=volare))
            # 超过波动率
            if abs(volare) > self.expectVolare: 
                if volare > 0 : # 满足代表 波动率为+
                    # 如果收益率超过 最大损失的5倍 则平仓
                    if volare > self.maxLoass * 5 : self.closePositionDirection(info['positionAmt'])
                    if info['notional'] != "0": #开仓
                        responseRate = round(float(info['unRealizedProfit']) / leverage / abs(float(info['notional'])),3)  # 盈利率
                        # 做多 加仓
                        if self.judge_direction(info['positionAmt']) and responseRate >= self.smallProfit: 
                            print("加仓！")
                            msg.buy_limit_msg(self.symbol,self.amount/4,curPrice)   
                        # 持仓量 != 一手的买入量
                        # elif not self.judge_is_firstPosition(info["positionAmt"]):
                        #     print("减仓！")
                        #     msg.buy_limit_msg(self.symbol,self.amount)                                                                 
                    else:
                        print("做多开仓")    
                        msg.buy_limit_msg(self.symbol,self.amount,curPrice)                            
                
                else: # 波动率为 负
                    
                    if info['notional'] != "0": # 开仓
                        # 做多 加仓
                        responseRate = round(float(info['unRealizedProfit']) / leverage / abs(float(info['notional'])),3)  # 盈利率
                        if not self.judge_direction(info['positionAmt']) and responseRate >= self.smallProfit: 
                            print("加仓！")
                            msg.sell_limit_msg(self.symbol,self.amount/4,curPrice)   # 加仓只加25%
                        # 持仓量 != 一手的买入量
                        # elif not self.judge_is_firstPosition(info["positionAmt"]):
                        #     print("减仓！")
                        #     msg.buy_limit_msg(self.symbol,self.amount)                                                                 
                    else:
                        print("做空开仓")    
                        msg.sell_limit_msg(self.symbol,self.amount,curPrice)  
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
    #while True:
    #    ins.run()