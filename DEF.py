class BATH1:
    ID = '1'
    TMP_list =[1 for i in range(48)]
    DO_list = [1 for i in range(48)]
    PH_list = [1 for i in range(48)]
    DateTime_list = [0 for i in range(48)]
    WeekData_dict = {'TMP' : [0 for i in range(48)], 'DO' : [0 for i in range(48)],'PH':[0 for i in range(48)],'TIME':[0 for i in range(48)]}
    MonthData_dict =  {'TMP' : [0 for i in range(48)],'DO':[0 for i in range(48)],'PH':[0 for i in range(48)],'TIME':[0 for i in range(48)]}  
    Level = 0
    HEATER = 'ON'
    PUMP = 'OFF'

class BATH2:
    ID = '2'
    TMP_list = [2 for i in range(48)]
    DO_list = [2 for i in range(48)]
    PH_list = [2 for i in range(48)]
    DateTime_list = [0 for i in range(48)]
    WeekData_dict = {'TMP' : [0 for i in range(48)], 'DO' : [0 for i in range(48)],'PH':[0 for i in range(48)],'TIME':[0 for i in range(48)]}
    MonthData_dict =  {'TMP' : [0 for i in range(48)],'DO':[0 for i in range(48)],'PH':[0 for i in range(48)],'TIME':[0 for i in range(48)]}  
    Level = 0
    HEATER = 'OFF'
    PUMP = 'OFF'

class BATH3:
    ID = '3'
    TMP_list = [3 for i in range(48)]
    DO_list = [3 for i in range(48)]
    PH_list = [3 for i in range(48)]
    DateTime_list = [0 for i in range(48)]
    WeekData_dict = {'TMP' : [0 for i in range(48)], 'DO' : [0 for i in range(48)],'PH':[0 for i in range(48)],'TIME':[0 for i in range(48)]}
    MonthData_dict =  {'TMP' : [0 for i in range(48)],'DO':[0 for i in range(48)],'PH':[0 for i in range(48)],'TIME':[0 for i in range(48)]} 
    Level = 0
    HEATER = 'OFF'
    PUMP = 'OFF'

class BATH4:
    ID = '4'
    TMP_list = [4 for i in range(48)]
    DO_list = [4 for i in range(48)]
    PH_list = [4 for i in range(48)]
    DateTime_list = [0 for i in range(48)]
    WeekData_dict = {'TMP' : [0 for i in range(48)], 'DO' : [0 for i in range(48)],'PH':[0 for i in range(48)],'TIME':[0 for i in range(48)]}
    MonthData_dict =  {'TMP' : [0 for i in range(48)],'DO':[0 for i in range(48)],'PH':[0 for i in range(48)],'TIME':[0 for i in range(48)]} 
    Level = 0
    HEATER = 'OFF'
    PUMP = 'OFF'

class SENSOR:
    OUTTMP_list = [0 for i in range(48)]
    OUTTMP_DateTime_list = [0 for i in range(48)]

    INTMP_list = [0 for i in range(48)]
    INHUMID_list = [0 for i in range(48)] ## 실내 습도
    CO2_list = [0 for i in range(48)]
    LUX_list = [0 for i in range(48)]
    SENSORS_DateTime_list = [0 for i in range(48)]

    AMMONIA_list = [0 for i in range(48)]
    EC = 0
    
    ELECTRON_list = [0 for i in range(48)]
    ELECTRON_dict = {'1hour':0, '1day':0, '1week':0, '1month':0}
    ELECTRON_DateTime_list = [0 for i in range(48)]
    BLACKOUTcnt = 0
    
    WeekData_dict = {'OUTTMP' : [], 'TIME_outtmp':[],
                    'INTMP': [], 'INHUMID':[],'CO2':[], 'LUX':[],
                    'AMMONIA':[], 'EC':[], 'TIME_sensors':[],
                    'ELECTRON':[2 for i in range(48)], 'TIME_electron':[0 for i in range(48)]}
    MonthData_dict = {'OUTTMP' : [], 'TIME_outtmp':[],
                    'INTMP': [], 'INHUMID':[],'CO2':[], 'LUX':[],
                    'AMMONIA':[], 'EC':[], 'TIME_sensors':[],
                    'ELECTRON':[1 for i in range(48)], 'TIME_electron':[0 for i in range(48)]}

class ACTUATOR:
    AIR = {'power' : 'OFF', 'auto' : 'O'} 
    WIND = {'power' :'OFF', 'auto' : 'O'}
    LED = {'power':'OFF', 'auto' : 'O'}
    UV = {'power':'OFF', 'auto' : 'O'}


class SETTINGS:
    INTMP = {'from' : 0, 'to':100}
    CO2 = {'from' : 0, 'to':5000}
    INLUX = {'from' : 0, 'to':100}
    EC = {'from' : 0, 'to':100}
    INHUMID = {'from' : 0, 'to':100}
    AMMONIA = {'from' : 0, 'to':100}
    ELECTRON = {'delay' : 'X', 'month':'X','blackout':'X'}
    BATH_dict = {'BATH1' : { 'check': 'O', 'TMP' : {'from' :0 , 'to' : 100 }, 'DO':{'from' : 0, 'to' : 100}, 'PH' : {'from' : 0, 'to':14}},
                'BATH2' : { 'check': 'O', 'TMP' : {'from' :0 , 'to' : 100 }, 'DO':{'from' : 0, 'to' : 100}, 'PH' : {'from' : 0, 'to':14}},
                'BATH3' : { 'check': 'O', 'TMP' : {'from' :0 , 'to' : 100 }, 'DO':{'from' : 0, 'to' : 100}, 'PH' : {'from' : 0, 'to':14}},
                'BATH4' : { 'check': 'O', 'TMP' : {'from' :0 , 'to' : 100 }, 'DO':{'from' : 0, 'to' : 100}, 'PH' : {'from' : 0, 'to':14}},
                'BATH5' : { 'check': 'X', 'TMP' : {'from' :0 , 'to' : 100 }, 'DO':{'from' : 0, 'to' : 100}, 'PH' : {'from' : 0, 'to':14}},
                'BATH6' : { 'check': 'X', 'TMP' : {'from' :0 , 'to' : 100 }, 'DO':{'from' : 0, 'to' : 100}, 'PH' : {'from' : 0, 'to':14}},
                'BATH7' : { 'check': 'X', 'TMP' : {'from' :0 , 'to' : 100 }, 'DO':{'from' : 0, 'to' : 100}, 'PH' : {'from' : 0, 'to':14}},
                'BATH8' : { 'check': 'X', 'TMP' : {'from' :0 , 'to' : 100 }, 'DO':{'from' : 0, 'to' : 100}, 'PH' : {'from' : 0, 'to':14}}}
    FREQ1 = 10
    UNIT1 = '초'
    FREQ2 = 10
    UNIT2 = '초'
    IP = '127.0.0.1'
    PORT = '3306'
    lastTime = '2018-12-31 12:59:59'
    
bathDef_list = [BATH1, BATH2, BATH3, BATH4]
sensorDef_list = [SENSOR.INTMP_list, SENSOR.INHUMID_list, SENSOR.CO2_list, SENSOR.LUX_list]
