import os,json
# linux
data_path = os.getcwd()+"/data/data.json"
# 本地调试
# data_path = os.getcwd()+""+"/data/data.json"
# windows
# data_path = os.getcwd() + "\data\data.json"

class RunBetData():

    def _get_json_data(self):
        '''读取json文件'''
        tmp_json = {}
        with open(data_path, 'r') as f:
            tmp_json = json.load(f)
            f.close()
        return tmp_json


    def _modify_json_data(self,data):
        '''修改json文件'''
        with open(data_path, "w") as f:
            f.write(json.dumps(data, indent=4))
        f.close()
        
    def get_orderId(self):
        data_json = self._get_json_data()
        return data_json['orderId']    

    def get_openLeverageBase(self):
        '''限制提高杠杆的门槛，满足杠杆数*该系数才能增加杠杆'''
        data_json = self._get_json_data()
        return data_json['openLeverageBase'] 
    
    def get_maxLoss(self):
        '''一倍杠杆的情况下最多亏损比率'''
        data_json = self._get_json_data()
        return data_json['openLeverageBase']         
    
    def get_amount(self):
        '''获取交易数量'''
        data_json = self._get_json_data()
        return data_json['amount']    
    
    def get_expectVolare(self):
        '''预期波动率'''
        data_json = self._get_json_data()
        return data_json['expectVolare'] 
        
    def set_orderId(self,id):
        data_json = self._get_json_data()
        data_json['orderId'] = id
        self._modify_json_data(data_json)            
    
    def get_symbol(self):
        data_json = self._get_json_data()
        return data_json['symbol']   
    
    def get_waitTime(self):
        data_json = self._get_json_data()
        return data_json['waitTime'] 
    
if __name__ == "__main__":
    ins = RunBetData()
    print(ins.get_symbol())        
