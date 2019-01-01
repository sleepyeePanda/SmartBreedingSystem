from control_gui import *
from DEF import *
from StyleSheet import *
import PyQt5
import pyqtgraph as pg
import sys
import glob
import serial
import asyncio
import serial_asyncio
from threading import Thread
import time
import datetime
import json
from functools import partial
import pymysql

# parameter placeholder
INSERT_BATHquery = "INSERT INTO control_values(ID, bathID, TMP, DO, PH, DateTime) VALUES(%s, %s, %s, %s, %s, %s)"

# delete
#INSERT_BATHquery = "INSERT INTO control_values(ID, bathID, TMP, DO, PH, EC, DateTime) VALUES(%s, %s, %s, %s, %s, %s)"

INSERT_OUTSIDEquery = "INSERT INTO control_values(ID, OUTTMP, DateTime) VALUES(%s, %s, %s)"
INSERT_INSIDEquery = "INSERT INTO control_values(ID, INTMP, INHUMID, CO2, LUX, DateTime) VALUES(%s, %s, %s, %s, %s, %s)"
INSERT_ELECTRONquery = "inert INTO control_values(ID, ELEC, DateTime) VALUES(%s, %s, %s)"

FETCH_LASTquery = "SELECT DateTime FROM control_values ORDER BY DateTime DESC LIMIT 1"

FETCH_BATHquery = "SELECT TMP, DO, PH, DateTime\
                    FROM control_values\
                    WHERE bathID = %s\
                    AND TMP IS NOT NULL\
                    AND DO IS NOT NULL\
                    AND PH IS NOT NULL\
                    AND DateTime IS NOT NULL\
                    ORDER BY DateTime DESC\
                    LIMIT 48"
FETCH_BATHquery_ = "SELECT AVG(TMP), AVG(DO), AVG(PH), DateTime\
                    FROM control_values\
                    WHERE bathID = %s"

FETCH_OUTSIDEquery = "SELECT OUTTMP, DateTime\
                    FROM control_values\
                    WHERE ID = %s\
                    AND OUTTMP IS NOT NULL\
                    AND DateTime Is NOT NULL\
                    ORDER BY DateTime DESC\
                    LIMIT 48"
FETCH_OUTSIDEquery_ = "SELECT AVG(OUTTMP), DateTime\
                        FROM control_values\
                        WHERE ID = %s"
                        
FETCH_INSIDEquery = "SELECT INTMP, INHUMID, CO2, LUX, DateTime\
                        FROM control_values\
                        WHERE ID = %s\
                        AND INTMP IS NOT NULL\
                        AND INHUMID IS NOT NULL\
                        AND CO2 IS NOT NULL\
                        AND LUX IS NOT NULL\
                        AND DateTime IS NOT NULL\
                        ORDER BY DateTime DESC\
                        LIMIT 48"                        
FETCH_INSIDEquery_ = "SELECT AVG(INTMP), AVG(INHUMID), AVG(CO2), AVG(LUX), DateTime\
                        FROM control_values\
                        WHERE ID = %s"

FETCH_ELECTRONquery = "SELECT ELEC, DateTime\
                        FROM control_values\
                        WHERE ID = %s\
                        AND ELEC IS NOT NULL\
                        AND DateTime IS NOT NULL\
                        ORDER BY DateTime DESC\
                        LIMIT 48"
FETCH_ELECTRONquery_ = "SELECT AVG(ELEC), DateTime\
                        FROM control_values\
                        WHERE ID = %s"
FETCH_ELECTRONquery_byHour = 'SELECT SUM(ELEC)\
                                FROM control_values\
                                GROUP BY DATE(DateTime), HOUR(DateTime)\
                                ORDER BY DateTime DESC\
                                LIMIT 1'
FETCH_ELECTRONquery_byDay = 'SELECT SUM(ELEC)\
                                FROM control_values\
                                GROUP BY DATE(DateTime)\
                                ORDER BY DateTime DESC\
                                LIMIT 1'
FETCH_ELECTRONquery_byWeek = "SELECT SUM(ELEC), DATE_FORMAT(DATE_SUB(DateTime, INTERVAL (DAYOFWEEK(DateTime)-1) DAY), '%Y-%m-%d') as start,\
                                DATE_FORMAT(DATE_SUB(DateTime, INTERVAL (DAYOFWEEK(DateTime)-7) DAY), '%Y-%m-%d') as end,\
                                DATE_FORMAT(DateTime, '%Y%U') AS date\
                                FROM control_values\
                                GROUP BY date\
                                ORDER BY DateTime DESC\
                                LIMIT 1"
FETCH_ELECTRONquery_byMonth = 'SELECT SUM(ELEC)\
                                FROM control_values\
                                GROUP BY MONTH(DateTime)\
                                ORDER BY DateTime DESC\
                                LIMIT 1'

byWeek= " GROUP BY DATE(DateTime), HOUR(DateTime)\
        ORDER BY DateTime DESC\
        LIMIT 168"

byMonth = " GROUP BY DATE(DateTime), HOUR(DateTime)\
        HAVING HOUR(DateTime) = %s OR\
        HOUR(DateTime) = %s OR\
        HOUR(DateTime) = %s OR\
        HOUR(DateTime) = %s\
        ORDER BY DateTime DESC\
        LIMIT 168"


hours = [[hour for hour in range(24) if hour%6 == 0],
        [hour for hour in range(24) if hour%6 == 1],
        [hour for hour in range(24) if hour%6 == 2],
        [hour for hour in range(24) if hour%6 == 3],
        [hour for hour in range(24) if hour%6 == 4],
        [hour for hour in range(24) if hour%6 == 5]]

class DBInsertManager(PyQt5.QtCore.QThread):
    
    def __init__(self):
        super().__init__()
        # self.get_connection()
        # self.fetchLastData()
        # self.fetchBATHData(1)
        # self.fetchBATHData(2)
        # self.fetchBATHData(3)
        # self.fetchBATHData(4)
        # self.fetchSENSORData('outside')
        # self.fetchSENSORData('inside')
        # self.fetchSENSORData('electron')
        self.start()

    def get_connection(self):
        # MySQL Connection 연결
        self.connection = pymysql.connect(host='localhost', user='user1_insert', password='insert_0', db='control_db', charset='utf8')

    def fetchLastData(self):
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute(FETCH_LASTquery)
            SETTINGS.lastTime = cursor.fetchmany(1)[0][0].strftime('%Y-%m-%d %H:%M:%S')

    def fetchBATHData(self, bathID):
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute(FETCH_BATHquery,(bathID))
            rows = cursor.fetchall()
            for row in rows:
                bathDef_list[bathID-1].TMP_list.append(row[0])
                bathDef_list[bathID-1].TMP_list.pop(0)
                bathDef_list[bathID-1].DO_list.append(row[1])
                bathDef_list[bathID-1].DO_list.pop(0)
                bathDef_list[bathID-1].PH_list.append(row[2])
                bathDef_list[bathID-1].PH_list.pop(0)
                bathDef_list[bathID-1].DateTime_list.append(str(row[3])[-9:])
                bathDef_list[bathID-1].DateTime_list.pop(0)
                #del
                #bathDef_list[bathID-1].DateTime_list.append(row[3]))
                #bathDef_list[bathID-1].DateTime_list.pop(0)
                #bathDef_list[bathID-1].DateTime_list.append(str(row[4])[-9:])
                #bathDef_list[bathID-1].DateTime_list.pop(0)
            bathDef_list[bathID-1].DateTime_list.sort(reverse = True)

    def fetchSENSORData(self, sensor):
        if self.connection:
            cursor = self.connection.cursor()
            if sensor == 'outside':
                print('outside')
                cursor.execute(FETCH_OUTSIDEquery, 'outside')
                rows = cursor.fetchall()
                for row in rows:
                    SENSOR.OUTTMP_list.append(row[0])
                    SENSOR.OUTTMP_list.pop(0)
                    SENSOR.OUTTMP_DateTime_list.append(str(row[1])[-9:])
                    SENSOR.OUTTMP_DateTime_list.pop(0)
                print(SENSOR.OUTTMP_list)
                SENSOR.OUTTMP_DateTime_list.sort(reverse = True)
            elif sensor == 'inside':
                cursor.execute(FETCH_INSIDEquery, 'inside')
                rows = cursor.fetchall()
                for i, sensor_list in enumerate(sensorDef_list):
                    for row in rows:
                        sensor_list.append(row[i])
                        sensor_list.pop(0)
                for row in rows:
                    SENSOR.SENSORS_DateTime_list.append(str(row[4])[-9:])
                    SENSOR.SENSORS_DateTime_list.pop(0)
                SENSOR.SENSORS_DateTime_list.sort(reverse = True)
            elif sensor == 'electron':
                cursor.execute(FETCH_ELECTRONquery,'electron')
                rows = cursor.fetchall()
                for row in rows:
                    SENSOR.ELECTRON_list.append(row[0])      
                    SENSOR.ELECTRON_list.pop(0)
                    SENSOR.ELECTRON_DateTime_list.append(str(row[1])[-9:])
                    SENSOR.ELECTRON_DateTime_list.pop(0)
                SENSOR.ELECTRON_DateTime_list.sort(reverse = True)


    @PyQt5.QtCore.pyqtSlot(dict, str)
    def insertData(self, values, sensor):
        if self.connection:
            # Connection 으로부터 Cursor 생성
            # Array based cursor : return tuple after exectuing SQL 
            try:
                cursor = self.connection.cursor()
                if sensor == 'bath':
                    #del
                    #cursor.execute(INSERT_BATHquery,(values['ID'],values['bathID'],values['TMP'], values['DO'],values['PH'], values['EC'],values['DateTime']))
                    cursor.execute(INSERT_BATHquery,(values['ID'],values['bathID'],values['TMP'], values['DO'],values['PH'], values['DateTime']))
                    self.connection.commit()
                elif sensor == 'outside':
                    cursor.execute(INSERT_OUTSIDEquery,(values['ID'],values['OUTTMP'], values['DateTime']))
                    self.connection.commit()
                elif sensor == 'inside':
                    cursor.execute(INSERT_INSIDEquery,(values['ID'], values['INTMP'], values['INHUMID'], values['CO2'], values['LUX'], values['DateTime']))
                    self.connection.commit()
                elif sensor == 'electron':
                    cursor.execute(INSERT_ELECTRONquery, (values['ID'], values['ELEC'], values['DateTime']))
                    self.connection.commit()
            except Exception as e:
                print(str(e))

    def disconnect(self):
        #connection 닫기
        if self.connection.open:
            self.connection.close()
            print('inserting DB disconnected!')

class DBFetchManager(PyQt5.QtCore.QThread):
    fetchBathOldDataSignal = PyQt5.QtCore.pyqtSignal(int, bool)
    fetchSensorOldDataSignal = PyQt5.QtCore.pyqtSignal(bool, int)
    fetchElectronOldDataSignal = PyQt5.QtCore.pyqtSignal(bool)
    fetchElectronStatSignal = PyQt5.QtCore.pyqtSignal()
     
    def __init__(self, ui, eventThread):
        super().__init__()
        # self.eventThread = eventThread
        # self.ui = ui
        # self.get_connection()
        # self.fetchELEC_StatData()
        # for i in range(4):
        #     eventThread.radioButton_list[1][i].clicked.connect(partial(self.fetchBATH_OldData,i+1,'week',bathDef_list[i].WeekData_dict))
        #     eventThread.radioButton_list[2][i].clicked.connect(partial(self.fetchBATH_OldData,i+1,'month',bathDef_list[i].MonthData_dict))
        # ui.radioButton_airweek1.clicked.connect(partial(self.fetchSENSOR_OldData,'sensors', 'week', SENSOR.WeekData_dict))
        # ui.radioButton_airweek2.clicked.connect(partial(self.fetchSENSOR_OldData,'sensors', 'week', SENSOR.WeekData_dict))
        # ui.radioButton_elecweek.clicked.connect(partial(self.fetchSENSOR_OldData,'electron', 'week', SENSOR.WeekData_dict))
        # ui.radioButton_airmonth1.clicked.connect(partial(self.fetchSENSOR_OldData,'sensors', 'month', SENSOR.MonthData_dict))
        # ui.radioButton_airmonth2.clicked.connect(partial(self.fetchSENSOR_OldData,'sensors', 'month', SENSOR.MonthData_dict))
        # ui.radioButton_elecmonth.clicked.connect(partial(self.fetchSENSOR_OldData,'electron', 'month', SENSOR.MonthData_dict))
        # self.fetchBathOldDataSignal.connect(eventThread.updateBATHPlot)
        # self.fetchSensorOldDataSignal.connect(eventThread.updateAirConditionPlot)
        # self.fetchElectronOldDataSignal.connect(eventThread.updateELECPlot)
        # self.fetchElectronStatSignal.connect(eventThread.updateELEC)
        # self.timer = PyQt5.QtCore.QTimer()
        # self.timer.timeout.connect(self.fetchELEC_StatData)
        # self.timer.start(1000*60*60)
        self.start()

    def get_connection(self):
        # MySQL Connection 연결
        self.connection = pymysql.connect(host='localhost', user='root', password='Thgus69!', db='control_db', charset='utf8')
    
    @PyQt5.QtCore.pyqtSlot(int, str, dict)
    def fetchBATH_OldData(self, bathID, period, dictionary):
        if period == 'week':
            by = byWeek
            parameter = (bathID)
        else :
            by = byMonth
            parameter = (bathID,) + tuple(hours[int(datetime.datetime.now().strftime('%H'))%6])
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute(FETCH_BATHquery_+by,parameter)
            rows = cursor.fetchall()
            dictionary['TMP']=[row[0] for row in rows]
            dictionary['DO']=[row[1] for row in rows]
            dictionary['PH'] =[row[2] for row in rows]
            dictionary['TIME']=[str(row[3])[-14:-6] for row in rows]
            #del
            #dictionary['EC'] = rows[-1][3] 
            #dictionary['TIME'] = [str(row[4])[-14:-6] for row in rows]
        self.fetchBathOldDataSignal.emit(bathID-1,False)

    @PyQt5.QtCore.pyqtSlot(str, str, dict)
    def fetchSENSOR_OldData(self, sensor, period, dictionary):
        if self.connection:
            cursor1 = self.connection.cursor()
            cursor2 = self.connection.cursor()
            if sensor == 'sensors':
                if period == 'week':
                    cursor1.execute(FETCH_OUTSIDEquery_+byWeek, 'outside')
                else:
                    cursor1.execute(FETCH_OUTSIDEquery_+byMonth, ('outside',)+tuple(hours[int(datetime.datetime.now().strftime('%H'))%6]))
                rows1 = cursor1.fetchall()
                dictionary['OUTTMP'] = [row[0] for row in rows1]
                dictionary['TIME_outtmp'] = [str(row[1])[-14:-6] for row in rows1]
                if period == 'week':
                    cursor2.execute(FETCH_INSIDEquery_+byWeek,'inside')
                else:
                    cursor2.execute(FETCH_INSIDEquery_+byMonth,('inside',)+tuple(hours[int(datetime.datetime.now().strftime('%H'))%6]))
                rows2 = cursor2.fetchall()
                dictionary['INTMP'] = [row[0] for row in rows2]
                dictionary['INHUMID'] = [row[1] for row in rows2]
                dictionary['CO2'] = [row[2] for row in rows2]
                dictionary['LUX'] = [row[3] for row in rows2]
                dictionary['TIME_sensors'] = [str(row[4])[-14:-6] for row in rows2]
                # dictionary['AMMONIA'].append(row[1])
                # dictionary['AMMONIA'].pop(0)
                # dictionary['EC'].append(row[1])
                # dictionary['EC'].pop(0)
                if not ui.radioButton_airday1.isChecked():
                    self.fetchSensorOldDataSignal.emit(False, 1)
                if not ui.radioButton_airday2.isChecked():
                    self.fetchSensorOldDataSignal.emit(False, 2)
            elif sensor == 'electron':
                if period == 'week':
                    cursor1.execute(FETCH_ELECTRONquery_+byWeek, 'electron')
                else:
                    cursor1.execute(FETCH_ELECTRONquery_+byMonth, ('electron',)+tuple(hours[int(datetime.datetime.now().strftime('%H'))%6]))
                rows = cursor1.fetchall()
                dictionary['ELECTRON']=[row[0] for row in rows]
                dictionary['TIME_electron']=[str(row[1])[-14:-6] for row in rows]
                self.fetchElectronOldDataSignal.emit(False)
    
    def fetchELEC_StatData(self):
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute(FETCH_ELECTRONquery_byHour)
            SENSOR.ELECTRON_dict['1hour'] = cursor.fetchall()[0][0]
            cursor.execute(FETCH_ELECTRONquery_byDay) 
            SENSOR.ELECTRON_dict['1day'] =  cursor.fetchall()[0][0]         
            cursor.execute(FETCH_ELECTRONquery_byWeek)
            SENSOR.ELECTRON_dict['1week'] = cursor.fetchall()[0][0]
            cursor.execute(FETCH_ELECTRONquery_byMonth)
            SENSOR.ELECTRON_dict['1month'] = cursor.fetchall()[0][0]
            self.fetchElectronStatSignal.emit()

    def disconnect(self):
        #connection 닫기
        if self.connection.open:
            self.connection.close()
            print('fetching DB disconnected!')

class UartCom():
    
    def __init__(self, ui, eventThread, dbInsertManagerThread):
        self.ui=ui
        self.get_com()
        self.controlButton_list = eventThread.controlButton_list
        self.eventThread = eventThread
        self.dbInsertManagerThread = dbInsertManagerThread

        ui.pushButton_comconnect.clicked.connect(lambda x:self.connect_serial())
        ui.pushButton_disconnect.clicked.connect(self.disconnect_serial)
        ui.pushButton_check.clicked.connect(lambda x: self.sendUart())
        ui.pushButton_airpower.clicked.connect(lambda x: self.controlAirpower())
        ui.pushButton_windpower.clicked.connect(lambda x: self.controlWindpower())
        ui.pushButton_ledpower.clicked.connect(lambda x: self.controlLEDpower())
        ui.pushButton_uvpower.clicked.connect(lambda x: self.controlUVpower())

        for i, controlButton in enumerate(self.controlButton_list):
            controlButton[0].clicked.connect(partial(self.controlPumppower, i+1, bathDef_list[i]))
            controlButton[1].clicked.connect(partial(self.controlHeaterpower, i+1, bathDef_list[i]))
        self.uart = None

    def get_com(self, waiting = 0):
        time.sleep(waiting)
        connect_port=[]
        if sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            self.isLinux = True
        else:
            self.isLinux = False
        COM_Ports=self.serial_ports()
        for port in COM_Ports:
            if port.find('COM') > -1:
                connect_port.append(port)
        print (connect_port)
        if not connect_port:
            eventThread.alert('통신 연결을 확인한 후 프로그램을 재실행 해주십시오')
        else:
            for comport in connect_port:
                ui.comboBox_coms.addItem(comport)

    def serial_ports(self):  
        if sys.platform.startswith('win'):   
            ports = ['COM%s' % (i + 1) for i in range(256)]   
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):   
            # this excludes your current terminal "/dev/tty"   
            ports = glob.glob('/dev/tty[A-Za-z]*')   
        elif sys.platform.startswith('darwin'):   
            ports = glob.glob('/dev/tty.*')   
        else:   
            raise EnvironmentError('Unsupported platform')   
        result = []   
        for port in ports:   
            try:   
                s = serial.Serial(port)   
                s.close()   
                result.append(port)   
            except (OSError, serial.SerialException):  
                pass
                #print ('OSError')   
        return result

    def run(self, loop):
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        print("Closed Uart thread!")

    def connect_serial(self):
        com_no = str(ui.comboBox_coms.currentText())
        print(com_no)
        if com_no:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

            if self.isLinux:
                self.coro = serial_asyncio.create_serial_connection(self.loop, lambda: UartProtocol(self, self.eventThread, self.dbInsertManagerThread), com_no, baudrate=115200)
                print(str(com_no)+' connected')
            else:
                self.coro = serial_asyncio.create_serial_connection(self.loop, lambda: UartProtocol(self, self.eventThread, self.dbInsertManagerThread), com_no, baudrate=115200)
                print(str(com_no)+' connected')
            self.loop.run_until_complete(self.coro)

            self.t = Thread(target=self.run, args=(self.loop,))
            self.t.start()
            ui.pushButton_comconnect.setText("연결 완료")
            ui.pushButton_comconnect.setChecked(True)
            ui.pushButton_comconnect.setEnabled(False)
            ui.comboBox_coms.setEnabled(False)
        else:
            ui.pushButton_comconnect.setText("연결")
            ui.pushButton_comconnect.setChecked(False)
            ui.comboBox_coms.setEnabled(True)

    def disconnect_serial(self):
        if self.uart != None:
            self.uart.loop.shutdown_asyncgens()
            self.uart.close()
            self.uart = None
        ui.comboBox_coms.clear()
        self.get_com(0.3)
        ui.pushButton_comconnect.setText("연결")
        ui.pushButton_comconnect.setChecked(False)
        ui.pushButton_comconnect.setEnabled(True)
        ui.comboBox_coms.setEnabled(True)

    def sendUart(self):
        if self.uart != None:
            self.sendT1()
            time.sleep(0.1)
            self.sendT2()
            time.sleep(0.1)
            self.sendWater()
            time.sleep(0.2)
            self.sendELEC()
            time.sleep(0.1)
    
    def sendT1(self):
        msg = '\x02T1TEMP?\x03\x0A\x0D'
        print(msg)
        if self.uart != None:
            self.uart.write(msg.encode())        
        else: 
            print('Not Connected')

    def sendT2(self):
        msg = '\x02T2TEMP?\x03\x0A\x0D'
        print(msg)
        if self.uart != None:
            self.uart.write(msg.encode())        
        else : 
            print('Not Connected')

    def sendWater(self):
        msg = '\x02WNWATER?\x03\x0A\x0D'
        print(msg)
        if self.uart != None:
            for i in range(1,5):
                self.uart.write(msg.replace('N', str(i)).encode())
                time.sleep(.05)      
        else : 
            print('Not Connected')
    
    def controlAirpower(self):
        if ACTUATOR.AIR['power'] == 'OFF':
            msg = '\x02B1BO\x03\x0A\x0D'
        else:
            msg = '\x02B1BX\x03\x0A\x0D'
        if self.uart != None:
            self.uart.write(msg.encode())
            print(msg)   
        else : 
            print('Not Connected')

    def controlWindpower(self):
        if ACTUATOR.WIND['power'] == 'OFF':
            msg = '\x02F1FO\x03\x0A\x0D'
        else:
            msg = '\x02F1FX\x03\x0A\x0D'
        if self.uart != None:
            self.uart.write(msg.encode())   
            print(msg) 
        else : 
            print('Not Connected')

    def controlLEDpower(self):
        if ACTUATOR.LED['power'] == 'OFF':
            msg = '\x02L00W255R255G255B255\x03\x0A\x0D'
        else:
            msg = '\x02L00W000R000G000B000\x03\x0A\x0D'
        if self.uart != None:
            self.uart.write(msg.encode())    
            print(msg)
        else : 
            print('Not Connected')

    def controlUVpower(self):
        if ACTUATOR.UV['power'] == 'OFF':
            msg = '\x02U1UO\x03\x0A\x0D'
        else:
            msg = '\x02U1UX\x03\x0A\x0D'
        if self.uart != None:
            self.uart.write(msg.encode())    
            print(msg)
        else : 
            print('Not Connected')

    def controlHeaterpower(self, ID, BATH):
        if BATH.HEATER == 'OFF':
            msg = '\x02H'+str(ID)+'HOL'+str(SETTINGS.BATH_dict['BATH'+str(ID)]['TMP']['from'])+\
            'H'+str(SETTINGS.BATH_dict['BATH'+str(ID)]['TMP']['to'])+'\x03\x0A\x0D'
        else:
            msg = '\x02H'+str(ID)+'HX\x03\x0A\x0D'
        if self.uart != None:
            self.uart.write(msg.encode())
            print(msg)
        else : 
            print('Not Connected')

    def controlPumppower(self, ID, BATH):
        if BATH.PUMP == 'OFF':
            msg = '\x02P'+str(ID)+'PO\x03\x0A\x0D'
        else:
            msg = '\x02P'+str(ID)+'PX\x03\x0A\x0D'
        if self.uart != None:
            self.uart.write(msg.encode())
            print(msg)
        else : 
            print('Not Connected')

    def sendELEC(self):
        msg = '\x02E1E1\x03\x0A\x0D'
        if self.uart != None:
            self.uart.write(msg.encode())
        else :
            print('Not Connected')



class UartProtocol(asyncio.Protocol):
    def __init__(self, uartCom, eventThread, dbInsertManagerThread):
        self.uartCom = uartCom
        self.rcvParser = RcvParser(uartCom, eventThread, dbInsertManagerThread)

    def connection_made(self, transport):
        self.transport = transport
        print('port opened', transport)
        # rts (Request to Send) : 송신 요청
        # cts (Clear to Send) : 송신 확인
        transport.serial.rts = False 
        self.uartCom.uart = transport

    def data_received(self, data):
        message = data.decode()
        print('data received', message)
        self.rcvParser.parsing(message)

    def connection_lost(self, exc):
        print('port closed')
        self.transport.loop.stop()
        #self.transport.loop.run_until_complete()
        
        #self.uartCom.connect_serial()

    def pause_writing(self):
        print('pause writing')
        print(self.transport.get_write_buffer_size())

    def resume_writing(self):
        print(self.transport.get_write_buffer_size())
        print('resume writing')


class RcvParser(PyQt5.QtCore.QObject):
    
    updateSensorSignal = PyQt5.QtCore.pyqtSignal(str)
    updatePowerSignal = PyQt5.QtCore.pyqtSignal(str)
    updateHeaterPowerSignal = PyQt5.QtCore.pyqtSignal(str)
    updatePumpPowerSignal = PyQt5.QtCore.pyqtSignal(str)
    updateWaterConditionSignal = PyQt5.QtCore.pyqtSignal(str)
    
    updateTMPSignal = PyQt5.QtCore.pyqtSignal()
    updateDOSignal = PyQt5.QtCore.pyqtSignal()
    updatePHSignal = PyQt5.QtCore.pyqtSignal()
    
    updateAirSignal = PyQt5.QtCore.pyqtSignal()
    updateELECSignal = PyQt5.QtCore.pyqtSignal()

    insertDBSignal = PyQt5.QtCore.pyqtSignal(dict, str)

    def __init__(self, uartCom, eventThread, dbInsertManagerThread):
        super().__init__()
        self.uartCom = uartCom
        self.dbInsertManagerThread = dbInsertManagerThread
        self.initProtocol()
        self.updateSensorSignal.connect(eventThread.updateSensor)
        self.updatePowerSignal.connect(eventThread.updateActuator)
        self.updateHeaterPowerSignal.connect(eventThread.updateHeater)
        self.updatePumpPowerSignal.connect(eventThread.updatePump)
        self.updateWaterConditionSignal.connect(eventThread.updateWaterCondition)
        self.updateTMPSignal.connect(eventThread.updateTMP)
        self.updateDOSignal.connect(eventThread.updateDO)
        self.updatePHSignal.connect(eventThread.updatePH)
        self.updateAirSignal.connect(eventThread.updateAircondition)
        self.updateELECSignal.connect(eventThread.updateELEC)
        #self.insertDBSignal.connect(dbInsertManagerThread.insertData)

    def parsing(self, pkt):
        self.command = pkt.strip("\x02\x03\n\r")
        cmd = self.command[0]
        try:
            func = self.protocol.get(cmd)
            return func(self.command)
        except Exception as e:
            print("Error{!r}, errorno is {}:".format(e, e.args[0]))

    def rcvT(self, command):
        print('data parsed ', command)
        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            index = command[1]
        except Exception as e:
            print(str(e))
            index = -1
        
        if index == '1':
            try : 
                outtmp = float(command[3:])
            except Exception as e:
                print(str(e))
                outtmp = SENSOR.OUTTMP_list[-1]  
            self.insertDBSignal.emit({'ID':'outside','OUTTMP':outtmp,'DateTime':time}, 'outside')
            SENSOR.OUTTMP_list.append(outtmp)
            SENSOR.OUTTMP_DateTime_list.append(time)
            self.updateSensorSignal.emit('outside')
            SENSOR.OUTTMP_list.pop(0)
            SENSOR.OUTTMP_DateTime_list.pop(0)
        elif index == '2':
            try:
                intmp = float(command[3:8])
            except Exception as e:
                print(str(e))
                intmp = SENSOR.INTMP_list[-1]
            try:
                inhumid = float(command[9:11])
            except Exception as e:
                print(str(e))
                inhumid = SENSOR.INHUMID_list[-1]
            try:
                co2 = float(command[12:16])
            except Exception as e:
                print(str(e))
                co2 = SENSOR.CO2_list[-1]
            try:
                lux = float(command[17:])
            except Exception as e:
                print(str(e))
                lux =SENSOR.LUX_list[-1]
            self.insertDBSignal.emit({'ID':'inside','INTMP':intmp, 'INHUMID': inhumid, 'CO2':co2, 'LUX':lux,'DateTime':time}, 'inside')
            SENSOR.INTMP_list.append(intmp)
            SENSOR.INHUMID_list.append(inhumid)
            SENSOR.CO2_list.append(co2)
            SENSOR.LUX_list.append(lux)            
            SENSOR.SENSORS_DateTime_list.append(time[-9:])
            self.updateSensorSignal.emit('inside')
            SENSOR.INTMP_list.pop(0)
            SENSOR.INHUMID_list.pop(0)
            SENSOR.CO2_list.pop(0)
            SENSOR.LUX_list.pop(0) 
            SENSOR.SENSORS_DateTime_list.pop(0)
        self.updateAirSignal.emit()

    def rcvWater(self, command):
        print('data parsed ', command)
        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try :
            index = int(command[1])-1
        except Exception as e:
            print(str(e))
            index=-1
        try:
            tmp = float(command[3:8])
        except Exception as e:
            print(str(e))
            tmp= bathDef_list[index].TMP_list[-1]
        try:
            do = float(command[9:13])
        except Exception as e:
            print(str(e))
            do = bathDef_list[index].DO_list[-1]
        try:
            ph = float(command[14:18])
        except Exception as e:
            print(str(e))
            ph = bathDef_list[index].PH_list[-1]
        try:
            # 동글 교체 후 주석 해제하여 코드 수정
            level = float(command[19:])
            #level = float(command[19:23])
        except Exception as e:
            print(str(e))
            level = bathDef_list[index].Level
        # 동글 교체 후 주석 해제하여 코드 수정
        # try :
        #     ec = float(command[24:])
        # except Exception as e:
        #     print(str(e))
        #     ec = -1
        # self.insertDBSignal.emit({'ID':'bath','bathID':index+1,'TMP':tmp,'DO':do,'PH':ph,'EC':ec,'DateTime':time}, 'bath')
        self.insertDBSignal.emit({'ID':'bath','bathID':index+1,'TMP':tmp,'DO':do,'PH':ph,'DateTime':time}, 'bath')

        bathDef_list[index].TMP_list.append(tmp)
        bathDef_list[index].DO_list.append(do)
        bathDef_list[index].PH_list.append(ph)
        #bathDef_list[index].EC = ec
        bathDef_list[index].Level = level
        bathDef_list[index].DateTime_list.append(time[-9:])
        self.updateWaterConditionSignal.emit('BATH'+str(index+1))
        self.updateTMPSignal.emit()
        self.updateDOSignal.emit()
        self.updatePHSignal.emit()
        bathDef_list[index].TMP_list.pop(0)
        bathDef_list[index].DO_list.pop(0)
        bathDef_list[index].PH_list.pop(0)
        bathDef_list[index].DateTime_list.pop(0)

    def rcvElectron(self, command):
        print('data parsed', command)
        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            electron = float(command[3:6])
        except Exception as e:
            print(str(e))
            electron = SENSOR.ELECTRON_list[-1]
        self.insertDBSignal.emit({'ID':'electron','ELEC':electron,'DateTime':time}, 'electron')
        SENSOR.ELECTRON_list.append(electron)
        SENSOR.ELECTRON_DateTime_list.append(time[-9:])
        self.updateELECSignal.emit()
        SENSOR.ELECTRON_list.pop(0)
        SENSOR.ELECTRON_DateTime_list.pop(0)

    def rcvAirpower(self, command):
        print('data parsed ', command)
        ACTUATOR.AIR['power'] = 'ON' if command[3]=='O' else 'OFF'
        self.updatePowerSignal.emit('air')

    def rcvWindpower(self, command):
        print('data parsed ', command)
        ACTUATOR.WIND['power'] = 'ON' if command[3]=='O' else 'OFF'
        self.updatePowerSignal.emit('wind')

    def rcvLEDpower(self, command):
        print('data parsed ', command)
        ACTUATOR.LED['power'] = 'ON' if command[3]=='O' else 'OFF'
        self.updatePowerSignal.emit('led')

    def rcvUVpower(self, command):
        print('data parsed ', command)
        ACTUATOR.UV['power'] = 'ON' if command[3]=='O' else 'OFF'
        self.updatePowerSignal.emit('uv')

    def rcvHeaterpower(self, command):
        print('data parsed ', command)
        if command[1] == '1':
            BATH1.HEATER = 'ON' if command[3]=='O' else 'OFF'
            self.updateHeaterPowerSignal.emit('BATH1')
        elif command[1] == '2':
            BATH2.HEATER = 'ON' if command[3]=='O' else 'OFF'
            self.updateHeaterPowerSignal.emit('BATH2')
        elif command[1] == '3':
            BATH3.HEATER = 'ON' if command[3]=='O' else 'OFF'
            self.updateHeaterPowerSignal.emit('BATH3')
        elif command[1] == '4':
            BATH4.HEATER = 'ON' if command[3]=='O' else 'OFF'
            self.updateHeaterPowerSignal.emit('BATH4')

    def rcvPumppower(self, command):
        print('data parsed ', command)
        if command[1] == '1':
            BATH1.PUMP = 'ON' if command[3]=='O' else 'OFF'
            self.updatePumpPowerSignal.emit('BATH1')
        elif command[1] == '2':
            BATH2.PUMP = 'ON' if command[3]=='O' else 'OFF'
            self.updatePumpPowerSignal.emit('BATH2')
        elif command[1] == '3':
            BATH3.PUMP = 'ON' if command[3]=='O' else 'OFF'
            self.updatePumpPowerSignal.emit('BATH3')
        elif command[1] == '4':
            BATH4.PUMP = 'ON' if command[3]=='O' else 'OFF'
            self.updatePumpPowerSignal.emit('BATH4')

    def initProtocol(self):
        self.protocol = {
        'T': self.rcvT,
        'W': self.rcvWater,
        'H': self.rcvHeaterpower,
        'P': self.rcvPumppower,
        'B': self.rcvAirpower,
        'F': self.rcvWindpower,
        'L': self.rcvLEDpower,
        'U': self.rcvUVpower,
        'E': self.rcvElectron
        }    


#QThread를 상속받는 시계 ui 업데이트 스레드
class TimeUpdateThread(PyQt5.QtCore.QThread):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.timer = PyQt5.QtCore.QTimer()
        self.timer.timeout.connect(self.changeTime)
        self.timer.start(1000)
        self.start()

    def changeTime(self):
        cur_time = PyQt5.QtCore.QTime.currentTime()
        ui.lcdNumber_hour.display(cur_time.toString('hh'))
        ui.lcdNumber_minute.display(cur_time.toString('mm'))
        ui.lcdNumber_second.display(cur_time.toString('ss'))
        cur_date = PyQt5.QtCore.QDate.currentDate()
        ui.label_timetitle.setText(cur_date.toString('yyyy년   MM월   dd일'))

class ValueUpdateThread(PyQt5.QtCore.QThread):
    def __init__(self, ui, uartcom, eventThread):
        super().__init__()
        self.ui = ui
        self.uartcom = uartcom
        self.eventThread = eventThread
        self.timer1 = PyQt5.QtCore.QTimer()
        self.timer1.timeout.connect(self.updateValue)
        self.freq = 10
        if SETTINGS.UNIT1 == 's':
            self.freq = SETTINGS.FREQ1*1000
        elif SETTINGS.UNIT1 == 'm':
            self.freq = SETTINGS.FREQ1*1000*60
        elif SETTINGS.UNIT1 == 'h':
            self.freq = SETTINGS.FREQ1*1000*60*60
        self.timer1.start(self.freq)
        self.start()

    def updateValue(self):
        if self.uartcom.uart != None:
            self.uartcom.sendUart()
            self.ui.label_lastchecktime.setText(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

class EventThread(PyQt5.QtCore.QThread):

    def __init__(self, ui):
        super().__init__()
        self.ui = ui        
        
        self.mainButton_list = [ui.pushButton_main,
                                ui.pushButton_watertmp, ui.pushButton_do, ui.pushButton_ph,
                                ui.pushButton_aircondition, ui.pushButton_electron, ui.pushButton_settings]
        self.pushButton_list =[ui.pushButton_check,
                                ui.pushButton_tmpvalue, ui.pushButton_tmpgraph,
                                ui.pushButton_dovalue, ui.pushButton_dograph,
                                ui.pushButton_phvalue, ui.pushButton_phgraph,
                                ui.pushButton_comconnect, ui.pushButton_disconnect,
                                ui.pushButton_applyall, ui.pushButton_save,
                                ui.pushButton_sensorsave1, ui.pushButton_sensorsave2, ui.pushButton_serversave,
                                ui.pushButton_intmpsave, ui.pushButton_co2save, ui.pushButton_luxsave, ui.pushButton_ecsave,
                                ui.pushButton_inhumidsave, ui.pushButton_ammoniasave, ui.pushButton_electronsave, ui.pushButton_othersave]
        self.tmplabel_list = [[ui.label_maintmp1,ui.label_maintmp2,ui.label_maintmp3,ui.label_maintmp4,
                            ui.label_maintmp5,ui.label_maintmp6,ui.label_maintmp7,ui.label_maintmp8],
                            [ui.label_lowtmp1, ui.label_lowtmp2, ui.label_lowtmp3, ui.label_lowtmp4,
                            ui.label_lowtmp5, ui.label_lowtmp6, ui.label_lowtmp7, ui.label_lowtmp8],
                            [ui.label_hightmp1, ui.label_hightmp2, ui.label_hightmp3, ui.label_hightmp4,
                            ui.label_hightmp5, ui.label_hightmp6, ui.label_hightmp7, ui.label_hightmp8]]
        self.dolabel_list =[[ui.label_maindo1,ui.label_maindo2,ui.label_maindo3,ui.label_maindo4,
                            ui.label_maindo5,ui.label_maindo6,ui.label_maindo7,ui.label_maindo8],
                            [ui.label_lowdo1, ui.label_lowdo2, ui.label_lowdo3, ui.label_lowdo4,
                            ui.label_lowdo5, ui.label_lowdo6, ui.label_lowdo7, ui.label_lowdo8],
                            [ui.label_highdo1, ui.label_highdo2, ui.label_highdo3, ui.label_highdo4,
                            ui.label_highdo5, ui.label_highdo6, ui.label_highdo7, ui.label_highdo8]]
        self.phlabel_list = [[ui.label_mainph1,ui.label_mainph2,ui.label_mainph3,ui.label_mainph4,
                            ui.label_mainph5,ui.label_mainph6,ui.label_mainph7,ui.label_mainph8],
                            [ui.label_lowph1, ui.label_lowph2, ui.label_lowph3, ui.label_lowph4,
                            ui.label_lowph5, ui.label_lowph6, ui.label_lowph7, ui.label_lowph8],
                            [ui.label_highph1, ui.label_highph2, ui.label_highph3, ui.label_highph4,
                            ui.label_highph5, ui.label_highph6, ui.label_highph7, ui.label_highph8]]
        self.bathlabel_list = [[ui.label_watertmp1, ui.label_do1,ui.label_ph1,ui.label_level1],
                                [ui.label_watertmp2, ui.label_do2,ui.label_ph2,ui.label_level2],
                                [ui.label_watertmp3, ui.label_do3,ui.label_ph3,ui.label_level3],
                                [ui.label_watertmp4, ui.label_do4,ui.label_ph4,ui.label_level4]]
        self.bathcheckbox_list = [ui.checkBox_1, ui.checkBox_2, ui.checkBox_3, ui.checkBox_4,
                                ui.checkBox_5, ui.checkBox_6, ui.checkBox_7, ui.checkBox_8]
        self.aircheckbox_list = [ui.checkBox_outtmp, ui.checkBox_intmp,ui.checkBox_inhumid, ui.checkBox_lux,
                                ui.checkBox_co2,ui.checkBox_ammonia]
        self.bathSpinBox_list = [[ui.doubleSpinBox_fromtmp1, ui.doubleSpinBox_totmp1,
                                ui.doubleSpinBox_fromdo1, ui.doubleSpinBox_todo1,
                                ui.doubleSpinBox_fromph1, ui.doubleSpinBox_toph1],
                                [ui.doubleSpinBox_fromtmp2, ui.doubleSpinBox_totmp2,
                                ui.doubleSpinBox_fromdo2, ui.doubleSpinBox_todo2,
                                ui.doubleSpinBox_fromph2, ui.doubleSpinBox_toph2],
                                [ui.doubleSpinBox_fromtmp3, ui.doubleSpinBox_totmp3,
                                ui.doubleSpinBox_fromdo3, ui.doubleSpinBox_todo3,
                                ui.doubleSpinBox_fromph3, ui.doubleSpinBox_toph3],
                                [ui.doubleSpinBox_fromtmp4, ui.doubleSpinBox_totmp4,
                                ui.doubleSpinBox_fromdo4, ui.doubleSpinBox_todo4,
                                ui.doubleSpinBox_fromph4, ui.doubleSpinBox_toph4]]
        self.controlButton_list = [[ui.pushButton_pumppower1, ui.pushButton_heaterpower1],
                                    [ui.pushButton_pumppower2, ui.pushButton_heaterpower2],
                                    [ui.pushButton_pumppower3, ui.pushButton_heaterpower3],
                                    [ui.pushButton_pumppower4, ui.pushButton_heaterpower4]]
        self.autoButton_lists = [[ui.pushButton_pumpauto1, ui.pushButton_heaterauto1],
                                    [ui.pushButton_pumpauto2, ui.pushButton_heaterauto2],
                                    [ui.pushButton_pumpauto3, ui.pushButton_heaterauto3],
                                    [ui.pushButton_pumpauto4, ui.pushButton_heaterauto4]]
        self.INITIALIZED_dict = {'bath1' : False,'bath2' : False,'bath3' : False,'bath4' : False,
                                'tmpgraph' : False , 'dograph' : False, 'phgraph' : False, 'settings': False,
                                'pump': False, 'heater':False, 'actuator':False, 'port':False}
        self.radioButton_list = [[ui.radioButton_day1, ui.radioButton_day2,ui.radioButton_day3, ui.radioButton_day4,
                                ui.radioButton_airday1,ui.radioButton_airday2, ui.radioButton_elecday],
                                [ui.radioButton_week1, ui.radioButton_week2, ui.radioButton_week3, ui.radioButton_week4,
                                ui.radioButton_airweek1, ui.radioButton_airweek2, ui.radioButton_elecweek],
                                [ui.radioButton_month1, ui.radioButton_month2, ui.radioButton_month3, ui.radioButton_month4,
                                ui.radioButton_airmonth1, ui.radioButton_airmonth2, ui.radioButton_elecmonth]]
        self.bathgraph_list = [ui.graphicsView_bathgraph1, ui.graphicsView_bathgraph2,
                                ui.graphicsView_bathgraph3, ui.graphicsView_bathgraph4]

        self.updateSettings()
        self.font10 = QtGui.QFont('맑은 고딕', 10)
        self.font11 = QtGui.QFont('맑은 고딕', 11)
        for pushButton in self.pushButton_list:
            pushButton.setStyleSheet(StyleSheet.pushButton)
        for i, mainButton in enumerate(self.mainButton_list):
            mainButton.setStyleSheet(StyleSheet.mainButton)
            # changePage
            mainButton.clicked.connect(partial(ui.stackedWidget.setCurrentIndex,i))

        ui.checkBox_outtmp.clicked.connect(lambda x: self.updateAirConditionPlot(True if ui.radioButton_airday1.isChecked() else False, 1))
        ui.checkBox_intmp.clicked.connect(lambda x: self.updateAirConditionPlot(True if ui.radioButton_airday1.isChecked() else False, 1))
        ui.checkBox_inhumid.clicked.connect(lambda x: self.updateAirConditionPlot(True if ui.radioButton_airday1.isChecked() else False, 1))
        ui.checkBox_lux.clicked.connect(lambda s: self.updateAirConditionPlot(True if ui.radioButton_airday1.isChecked() else False, 1))

        ui.checkBox_co2.clicked.connect(lambda x: self.updateAirConditionPlot(True if ui.radioButton_airday2.isChecked() else False, 2))
        ui.checkBox_ammonia.clicked.connect(lambda x:self.updateAirConditionPlot(True if ui.radioButton_airday2.isChecked() else False, 2))
        for i,radioButton in enumerate(self.radioButton_list[0][:4]):
            radioButton.clicked.connect(partial(self.updateBATHPlot, i))

        ui.radioButton_airday1.clicked.connect(partial(self.updateAirConditionPlot, True,1))
        ui.radioButton_airday2.clicked.connect(partial(self.updateAirConditionPlot, True, 2))

        ui.radioButton_elecday.clicked.connect(lambda x:self.updateELECPlot(True))
        ui.radioButton_elecweek.clicked.connect(lambda x:self.updateELECPlot(False))
        ui.radioButton_elecmonth.clicked.connect(lambda x: self.updateELECPlot(False))
        for i,autoButton_list in enumerate(self.autoButton_lists):
            for j, autoButton in enumerate(autoButton_list):
                autoButton.toggled.connect(partial(self.enable, autoButton, self.controlButton_list[i][j], True))

        ui.pushButton_airauto.clicked.connect(partial(self.enable, ui.pushButton_airauto, ui.pushButton_airpower, True))
        ui.pushButton_windauto.clicked.connect(partial(self.enable, ui.pushButton_windauto, ui.pushButton_windpower, False))
        ui.pushButton_ledauto.clicked.connect(partial(self.enable, ui.pushButton_ledauto, ui.pushButton_ledpower, True))
        ui.pushButton_uvauto.clicked.connect(partial(self.enable, ui.pushButton_uvauto, ui.pushButton_uvpower, False))

        for i in range(8):
            self.bathcheckbox_list[i].stateChanged.connect(partial(self.hideTab,i))

        ui.pushButton_check.clicked.connect(lambda x: ui.label_lastchecktime.setText(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        ui.pushButton_watertmp.clicked.connect(self.updateTMPPlot)
        ui.pushButton_do.clicked.connect(self.updateDOPlot)
        ui.pushButton_ph.clicked.connect(self.updatePHPlot)
        ui.pushButton_aircondition.clicked.connect(self.updateAircondition)
        ui.pushButton_electron.clicked.connect(self.updateELEC)
        ui.pushButton_settings.clicked.connect(lambda x : self.updateSettings(pushButton_clicked = True))
        # changeSubPage
        ui.pushButton_tmpvalue.clicked.connect(lambda x : ui.stackedWidget_1.setCurrentIndex(0))
        ui.pushButton_tmpgraph.clicked.connect(lambda x : ui.stackedWidget_1.setCurrentIndex(1))
        ui.pushButton_dovalue.clicked.connect(lambda x : ui.stackedWidget_2.setCurrentIndex(0))
        ui.pushButton_dograph.clicked.connect(lambda x : ui.stackedWidget_2.setCurrentIndex(1))
        ui.pushButton_phvalue.clicked.connect(lambda x : ui.stackedWidget_3.setCurrentIndex(0))
        ui.pushButton_phgraph.clicked.connect(lambda x : ui.stackedWidget_3.setCurrentIndex(1))
    
        for i,string in enumerate(['sensor1', 'sensor2','server', 'intmp', 'co2', 'lux', 'ec', 'inhumid', 'ammonia', 'electron']):  #other
            self.pushButton_list[11+i].clicked.connect(partial(self.updateSettings, sensor = string))
        ui.pushButton_sensorsave1.clicked.connect(lambda x: self.alert('프로그램 종료 후 재실행 시 적용됩니다.'))
        ui.pushButton_serversave.clicked.connect(lambda x: self.alert('프로그램 종료 후 재실행 시 적용됩니다.'))

        ui.pushButton_applyall.clicked.connect(lambda x: self.updateSettings(applyall_clicked= True))
        ui.pushButton_save.clicked.connect(lambda x: self.updateSettings(saveall_clicked=True))
        
        self.updateBATHPlot(0)
        self.updateBATHPlot(1)
        self.updateBATHPlot(2)
        self.updateBATHPlot(3)
        for i in range(1,5):
            self.updateWaterCondition('BATH'+str(i))
        self.updateActuator('INIT')
        self.updateSensor('outside')
        self.updateSensor('inside')
        self.updatePump('INIT')
        self.updateHeater('INIT')
        ui.label_lastchecktime.setText(SETTINGS.lastTime)
    
    def alert(self, message):
        msgBox = PyQt5.QtWidgets.QMessageBox()
        msgBox.setIcon(PyQt5.QtWidgets.QMessageBox.Information)
        msgBox.setText(message)
        msgBox.setStandardButtons(PyQt5.QtWidgets.QMessageBox.Ok | PyQt5.QtWidgets.QMessageBox.Cancel)
        subapp = msgBox.exec_()


    def hideTab(self,i):
        if self.bathcheckbox_list[i].isChecked():
            ui.tabWidget.setTabEnabled(i,True) 
        else:
             ui.tabWidget.setTabEnabled(i,False)
    
    def enable(self, pushButton,controlButton, white):
        if pushButton.isChecked() == True:
            pushButton.setText('자동')
            controlButton.setEnabled(False)
            if white:
                controlButton.setStyleSheet(StyleSheet.normallabel_whitebg+StyleSheet.disalbleButton)
            else:
                controlButton.setStyleSheet(StyleSheet.normallabel_greybg+StyleSheet.disalbleButton)
        else:
            pushButton.setText('수동')
            controlButton.setEnabled(True)
            if white:
                controlButton.setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)\
                if controlButton.text() == 'ON' else controlButton.setStyleSheet(StyleSheet.normallabel_whitebg)
            else :
                controlButton.setStyleSheet(StyleSheet.normallabel_greybg + StyleSheet.abnormaltext)\
                if controlButton.text() == 'ON' else controlButton.setStyleSheet(StyleSheet.normallabel_greybg)

    @PyQt5.QtCore.pyqtSlot(str) 
    def updateActuator(self, actuator):
        if self.INITIALIZED_dict['actuator'] == False:
            with open ('config.json', 'r') as jsonFile:
                actuatorData = json.load(jsonFile)["ACTUATOR"]
                ui.pushButton_airpower.setText(actuatorData["AIR"]["power"])
                ui.pushButton_airpower.setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)\
                if ui.pushButton_airpower.text() == 'ON' else ui.pushButton_airpower.setStyleSheet(StyleSheet.normallabel_whitebg)
                ui.pushButton_windpower.setText(actuatorData["WIND"]["power"])
                ui.pushButton_windpower.setStyleSheet(StyleSheet.normallabel_greybg + StyleSheet.abnormaltext)\
                if ui.pushButton_windpower.text() == 'ON' else ui.pushButton_windpower.setStyleSheet(StyleSheet.normallabel_greybg)
                ui.pushButton_ledpower.setText(actuatorData["LED"]["power"])
                ui.pushButton_ledpower.setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)\
                if ui.pushButton_ledpower.text() == 'ON' else ui.pushButton_ledpower.setStyleSheet(StyleSheet.normallabel_whitebg)
                ui.pushButton_uvpower.setText(actuatorData["UV"]["power"])
                ui.pushButton_uvpower.setStyleSheet(StyleSheet.normallabel_greybg + StyleSheet.abnormaltext)\
                if ui.pushButton_uvpower.text() == 'ON' else ui.pushButton_uvpower.setStyleSheet(StyleSheet.normallabel_greybg)
                self.INITIALIZED_dict['actuator'] = True
        elif actuator == 'air':
            ui.pushButton_airpower.setText(ACTUATOR.AIR['power'])
            ui.pushButton_airpower.setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)\
            if ACTUATOR.AIR['power'] == 'ON' else ui.pushButton_airpower.setStyleSheet(StyleSheet.normallabel_whitebg)
        elif actuator == 'wind':
            ui.pushButton_windpower.setText(ACTUATOR.WIND['power'])
            ui.pushButton_windpower.setStyleSheet(StyleSheet.normallabel_greybg + StyleSheet.abnormaltext)\
            if ACTUATOR.WIND['power'] == 'ON' else ui.pushButton_windpower.setStyleSheet(StyleSheet.normallabel_greybg)
        elif actuator == 'led':
            ui.pushButton_ledpower.setText(ACTUATOR.LED['power'])
            ui.pushButton_ledpower.setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)\
            if ACTUATOR.LED['power'] == 'ON' else ui.pushButton_ledpower.setStyleSheet(StyleSheet.normallabel_whitebg)
        elif actuator == 'uv':
            ui.pushButton_uvpower.setText(ACTUATOR.UV['power'])
            ui.pushButton_uvpower.setStyleSheet(StyleSheet.normallabel_greybg + StyleSheet.abnormaltext)\
            if ACTUATOR.UV['power'] == 'ON' else ui.pushButton_uvpower.setStyleSheet(StyleSheet.normallabel_greybg)

    @PyQt5.QtCore.pyqtSlot(str) 
    def updateSensor(self, sensor):
        if sensor == 'outside':
            ui.label_outtmp.setText(str(SENSOR.OUTTMP_list[-1]))
        elif sensor == 'inside':
            ui.label_intmp.setText(str(SENSOR.INTMP_list[-1]))
            if SENSOR.INTMP_list[-1] > SETTINGS.INTMP['to'] or SENSOR.INTMP_list[-1] < SETTINGS.INTMP['from']:
                ui.label_intmp.setStyleSheet(StyleSheet.normallabel_greybg + StyleSheet.abnormaltext)
            else :
                ui.label_intmp.setStyleSheet(StyleSheet.normallabel_greybg)
            ui.label_humid.setText(str(SENSOR.INHUMID_list[-1]))
            if SENSOR.INHUMID_list[-1] > SETTINGS.INHUMID['to'] or SENSOR.INHUMID_list[-1] < SETTINGS.INHUMID['from']:
                ui.label_humid.setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)
            else :
                ui.label_humid.setStyleSheet(StyleSheet.normallabel_whitebg)
            ui.label_co2.setText(str(SENSOR.CO2_list[-1]))
            if SENSOR.CO2_list[-1] > SETTINGS.CO2['to'] or SENSOR.CO2_list[-1] < SETTINGS.CO2['from']:
                ui.label_co2.setStyleSheet(StyleSheet.normallabel_greybg + StyleSheet.abnormaltext)
            else :
                ui.label_co2.setStyleSheet(StyleSheet.normallabel_greybg)
            ui.label_lux.setText(str(SENSOR.LUX_list[-1]))
            if SENSOR.LUX_list[-1] > SETTINGS.INLUX['to'] or SENSOR.LUX_list[-1] < SETTINGS.INLUX['from']:
                ui.label_lux.setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)
            else :
                ui.label_lux.setStyleSheet(StyleSheet.normallabel_whitebg)
            ui.label_ammonia.setText(str(SENSOR.AMMONIA_list[-1]))
            if SENSOR.AMMONIA_list[-1] > SETTINGS.AMMONIA['to'] or SENSOR.AMMONIA_list[-1] < SETTINGS.AMMONIA['from']:
                ui.label_ammonia.setStyleSheet(StyleSheet.normallabel_greybg + StyleSheet.abnormaltext)
            else :
                ui.label_ammonia.setStyleSheet(StyleSheet.normallabel_greybg)
            ui.label_ec.setText(str(SENSOR.EC))
            if SENSOR.EC > SETTINGS.EC['to'] or SENSOR.EC < SETTINGS.EC['from']:
                ui.label_ec.setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)
            else :
                ui.label_ec.setStyleSheet(StyleSheet.normallabel_whitebg)
            ui.label_blackout.setText(str(SENSOR.BLACKOUTcnt))

    @PyQt5.QtCore.pyqtSlot(str)
    def updatePump(self, BATH):
        if self.INITIALIZED_dict['pump'] == False:
            with open ('config.json', 'r') as jsonFile:
                data = json.load(jsonFile)
                for i, bath in enumerate(["BATH1", "BATH2", "BATH3", "BATH4"]):
                    self.controlButton_list[i][0].setText(data[bath]["PUMP"])
                    self.controlButton_list[i][0].setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)\
                    if self.controlButton_list[i][0].text() == 'ON' \
                    else self.controlButton_list[i][0].setStyleSheet(StyleSheet.normallabel_whitebg)
            self.INITIALIZED_dict['pump'] = True
        elif BATH == 'BATH1':
            ui.pushButton_pumppower1.setText(BATH1.PUMP)
            ui.pushButton_pumppower1.setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)\
            if BATH1.PUMP == 'ON' else ui.pushButton_pumppower1.setStyleSheet(StyleSheet.normallabel_whitebg)
        elif BATH == 'BATH2':
            ui.pushButton_pumppower2.setText(BATH2.PUMP)
            ui.pushButton_pumppower2.setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)\
            if BATH2.PUMP == 'ON' else ui.pushButton_pumppower2.setStyleSheet(StyleSheet.normallabel_whitebg)
        elif BATH == 'BATH3':
            ui.pushButton_pumppower3.setText(BATH3.PUMP)
            ui.pushButton_pumppower3.setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)\
            if BATH3.PUMP == 'ON' else ui.pushButton_pumppower3.setStyleSheet(StyleSheet.normallabel_whitebg)
        elif BATH == 'BATH4':
            ui.pushButton_pumppower4.setText(BATH4.PUMP)
            ui.pushButton_pumppower4.setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)\
            if BATH4.PUMP == 'ON' else ui.pushButton_pumppower4.setStyleSheet(StyleSheet.normallabel_whitebg)

    @PyQt5.QtCore.pyqtSlot(str)
    def updateHeater(self, BATH):
        if self.INITIALIZED_dict['heater'] == False:
            with open ('config.json', 'r') as jsonFile:
                data = json.load(jsonFile)
                for i, bath in enumerate(["BATH1", "BATH2", "BATH3", "BATH4"]):
                    self.controlButton_list[i][1].setText(data[bath]["HEATER"])
                    self.controlButton_list[i][1].setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)\
                    if self.controlButton_list[i][1].text() == 'ON' \
                    else self.controlButton_list[i][1].setStyleSheet(StyleSheet.normallabel_whitebg)
            self.INITIALIZED_dict['heater'] = True
        elif BATH == 'BATH1':
            ui.pushButton_heaterpower1.setText(BATH1.HEATER)
            ui.pushButton_heaterpower1.setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)\
            if BATH1.HEATER == 'ON' else ui.pushButton_heaterpower1.setStyleSheet(StyleSheet.normallabel_whitebg)
        elif BATH == 'BATH2':
            ui.pushButton_heaterpower2.setText(BATH2.HEATER)
            ui.pushButton_heaterpower2.setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)\
            if BATH2.HEATER == 'ON' else ui.pushButton_heaterpower2.setStyleSheet(StyleSheet.normallabel_whitebg)
        elif BATH == 'BATH3':
            ui.pushButton_heaterpower3.setText(BATH3.HEATER)
            ui.pushButton_heaterpower3.setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)\
            if BATH3.HEATER == 'ON' else ui.pushButton_heaterpower3.setStyleSheet(StyleSheet.normallabel_whitebg)
        elif BATH == 'BATH4':
            ui.pushButton_heaterpower4.setText(BATH4.HEATER)
            ui.pushButton_heaterpower4.setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)\
            if BATH4.HEATER == 'ON' else ui.pushButton_heaterpower4.setStyleSheet(StyleSheet.normallabel_whitebg)

    @PyQt5.QtCore.pyqtSlot(str)
    def updateWaterCondition(self, BATH):
        if BATH == 'BATH1':
            ui.label_watertmp1.setText(str(BATH1.TMP_list[-1]))
            if BATH1.TMP_list[-1] > SETTINGS.BATH_dict['BATH1']['TMP']['to'] or \
                BATH1.TMP_list[-1] < SETTINGS.BATH_dict['BATH1']['TMP']['from']:
                self.bathlabel_list[0][0].setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)
            else :
                self.bathlabel_list[0][0].setStyleSheet(StyleSheet.normallabel_whitebg)
            ui.label_do1.setText(str(BATH1.DO_list[-1]))
            if BATH1.DO_list[-1] > SETTINGS.BATH_dict['BATH1']['DO']['to'] or \
                BATH1.DO_list[-1] < SETTINGS.BATH_dict['BATH1']['DO']['from']:
                self.bathlabel_list[0][1].setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)
            else :
                self.bathlabel_list[0][1].setStyleSheet(StyleSheet.normallabel_whitebg)
            ui.label_ph1.setText(str(BATH1.PH_list[-1]))
            if BATH1.PH_list[-1] > SETTINGS.BATH_dict['BATH1']['PH']['to'] or \
                BATH1.PH_list[-1] < SETTINGS.BATH_dict['BATH1']['PH']['from']:
                self.bathlabel_list[0][2].setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)
            else :
                self.bathlabel_list[0][2].setStyleSheet(StyleSheet.normallabel_whitebg)
            ui.label_level1.setText(str(BATH1.Level))
            ui.label_level1.setStyleSheet(StyleSheet.normallabel_whitebg)
            self.updateBATHPlot(0)
        elif BATH == 'BATH2':
            ui.label_watertmp2.setText(str(BATH2.TMP_list[-1]))
            if BATH2.TMP_list[-1] > SETTINGS.BATH_dict['BATH2']['TMP']['to'] or \
                BATH2.TMP_list[-1] < SETTINGS.BATH_dict['BATH2']['TMP']['from']:
                self.bathlabel_list[1][0].setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)
            else :
                self.bathlabel_list[1][0].setStyleSheet(StyleSheet.normallabel_whitebg)
            ui.label_do2.setText(str(BATH2.DO_list[-1]))
            if BATH2.DO_list[-1] > SETTINGS.BATH_dict['BATH2']['DO']['to'] or \
                BATH2.DO_list[-1] < SETTINGS.BATH_dict['BATH2']['DO']['from']:
                self.bathlabel_list[1][1].setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)
            else :
                self.bathlabel_list[1][1].setStyleSheet(StyleSheet.normallabel_whitebg)
            ui.label_ph2.setText(str(BATH2.PH_list[-1]))
            if BATH2.PH_list[-1] > SETTINGS.BATH_dict['BATH2']['PH']['to'] or \
                BATH2.PH_list[-1] < SETTINGS.BATH_dict['BATH2']['PH']['from']:
                self.bathlabel_list[1][2].setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)
            else :
                self.bathlabel_list[1][2].setStyleSheet(StyleSheet.normallabel_whitebg)
            ui.label_level2.setText(str(BATH2.Level))
            ui.label_level2.setStyleSheet(StyleSheet.normallabel_whitebg)
            self.updateBATHPlot(1)
        elif BATH == 'BATH3':
            ui.label_watertmp3.setText(str(BATH3.TMP_list[-1]))
            if BATH3.TMP_list[-1] > SETTINGS.BATH_dict['BATH3']['TMP']['to'] or \
                BATH3.TMP_list[-1] < SETTINGS.BATH_dict['BATH3']['TMP']['from']:
                self.bathlabel_list[2][0].setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)
            else :
                self.bathlabel_list[2][0].setStyleSheet(StyleSheet.normallabel_whitebg)
            ui.label_do3.setText(str(BATH3.DO_list[-1]))
            if BATH3.DO_list[-1] > SETTINGS.BATH_dict['BATH3']['DO']['to'] or \
                BATH3.DO_list[-1] < SETTINGS.BATH_dict['BATH3']['DO']['from']:
                self.bathlabel_list[2][1].setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)
            else :
                self.bathlabel_list[2][1].setStyleSheet(StyleSheet.normallabel_whitebg)
            ui.label_ph3.setText(str(BATH3.PH_list[-1]))
            if BATH3.PH_list[-1] > SETTINGS.BATH_dict['BATH3']['PH']['to'] or \
                BATH3.PH_list[-1] < SETTINGS.BATH_dict['BATH3']['PH']['from']:
                self.bathlabel_list[2][2].setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)
            else :
                self.bathlabel_list[2][2].setStyleSheet(StyleSheet.normallabel_whitebg)
            ui.label_level3.setText(str(BATH3.Level))
            ui.label_level3.setStyleSheet(StyleSheet.normallabel_whitebg)
            self.updateBATHPlot(2)
        elif BATH == 'BATH4':
            ui.label_watertmp4.setText(str(BATH4.TMP_list[-1]))
            if BATH4.TMP_list[-1] > SETTINGS.BATH_dict['BATH4']['TMP']['to'] or \
                BATH4.TMP_list[-1] < SETTINGS.BATH_dict['BATH4']['TMP']['from']:
                self.bathlabel_list[3][0].setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)
            else :
                self.bathlabel_list[3][0].setStyleSheet(StyleSheet.normallabel_whitebg)
            ui.label_do4.setText(str(BATH4.DO_list[-1]))
            if BATH4.DO_list[-1] > SETTINGS.BATH_dict['BATH4']['DO']['to'] or \
                BATH4.DO_list[-1] < SETTINGS.BATH_dict['BATH4']['DO']['from']:
                self.bathlabel_list[3][1].setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)
            else :
                self.bathlabel_list[3][1].setStyleSheet(StyleSheet.normallabel_whitebg)
            ui.label_ph4.setText(str(BATH4.PH_list[-1]))
            if BATH4.PH_list[-1] > SETTINGS.BATH_dict['BATH4']['PH']['to'] or \
                BATH4.PH_list[-1] < SETTINGS.BATH_dict['BATH4']['PH']['from']:
                self.bathlabel_list[3][2].setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)
            else :
                self.bathlabel_list[3][2].setStyleSheet(StyleSheet.normallabel_whitebg)
            ui.label_level4.setText(str(BATH4.Level))
            ui.label_level4.setStyleSheet(StyleSheet.normallabel_whitebg)
            self.updateBATHPlot(3)


    def updateTMP(self):
        for i in range(4):
            self.tmplabel_list[0][i].setText(str(bathDef_list[i].TMP_list[-1]))
            self.tmplabel_list[1][i].setText(str(SETTINGS.BATH_dict['BATH'+str(i+1)]['TMP']['from']))
            self.tmplabel_list[2][i].setText(str(SETTINGS.BATH_dict['BATH'+str(i+1)]['TMP']['to'])) 
            if float(self.tmplabel_list[0][i].text()) > float(self.tmplabel_list[2][i].text()) or \
                float(self.tmplabel_list[0][i].text()) < float(self.tmplabel_list[1][i].text()):
                self.tmplabel_list[0][i].setStyleSheet(StyleSheet.abnormalback)
            else :
                self.tmplabel_list[0][i].setStyleSheet(StyleSheet.normalback)
        if ui.stackedWidget.currentIndex() == 1:
            self.updateTMPPlot()

    def updateDO(self):
        for i in range(4):
            self.dolabel_list[0][i].setText(str(bathDef_list[i].DO_list[-1]))
            self.dolabel_list[1][i].setText(str(SETTINGS.BATH_dict['BATH'+str(i+1)]['DO']['from']))
            self.dolabel_list[2][i].setText(str(SETTINGS.BATH_dict['BATH'+str(i+1)]['DO']['to']))
            if float(self.dolabel_list[0][i].text()) > float(self.dolabel_list[2][i].text()) or \
                float(self.dolabel_list[0][i].text()) < float(self.dolabel_list[1][i].text()):
                self.dolabel_list[0][i].setStyleSheet(StyleSheet.abnormalback)
            else :
                self.dolabel_list[0][i].setStyleSheet(StyleSheet.normalback)
        if ui.stackedWidget.currentIndex() == 2:
            self.updateDOPlot()

    def updatePH(self):
        for i in range(4):
            self.phlabel_list[0][i].setText(str(float(bathDef_list[i].PH_list[-1])))
            self.phlabel_list[1][i].setText(str(SETTINGS.BATH_dict['BATH'+str(i+1)]['PH']['from']))
            self.phlabel_list[2][i].setText(str(SETTINGS.BATH_dict['BATH'+str(i+1)]['PH']['to'])) 
            if float(self.phlabel_list[0][i].text()) > float(self.phlabel_list[2][i].text()) or \
                float(self.phlabel_list[0][i].text()) < float(self.phlabel_list[1][i].text()):
                self.phlabel_list[0][i].setStyleSheet(StyleSheet.abnormalback)
            else :
                self.phlabel_list[0][i].setStyleSheet(StyleSheet.normalback)
        if ui.stackedWidget.currentIndex() == 3:
            self.updatePHPlot()
          
    def updateAircondition(self, graph = 0):
        ui.label_outtmp2.setText(str(float(SENSOR.OUTTMP_list[-1])))
        ui.label_intmp2.setText(str(float(SENSOR.INTMP_list[-1])))
        if SENSOR.OUTTMP_list[-1] > SETTINGS.INTMP['to'] or SENSOR.OUTTMP_list[-1] < SETTINGS.INTMP['from']:
            ui.label_intmp2.setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)
        else :
            ui.label_intmp2.setStyleSheet(StyleSheet.normallabel_whitebg)
        ui.label_humid2.setText(str(float(SENSOR.INHUMID_list[-1])))
        if SENSOR.INHUMID_list[-1] > SETTINGS.INHUMID['to'] or SENSOR.INHUMID_list[-1] < SETTINGS.INHUMID['from']:
            ui.label_humid2.setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)
        else :
            ui.label_humid2.setStyleSheet(StyleSheet.normallabel_whitebg)
        ui.label_co22.setText(str(float(SENSOR.CO2_list[-1])))
        if SENSOR.CO2_list[-1] > SETTINGS.CO2['to'] or SENSOR.CO2_list[-1] < SETTINGS.CO2['from']:
            ui.label_co22.setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)
        else:
            ui.label_co22.setStyleSheet(StyleSheet.normallabel_whitebg)
        ui.label_ammonia2.setText(str(float(SENSOR.AMMONIA_list[-1])))
        if SENSOR.AMMONIA_list[-1] > SETTINGS.AMMONIA['to'] or SENSOR.AMMONIA_list[-1] < SETTINGS.AMMONIA['from']:
            ui.label_ammonia2.setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)
        else:
            ui.label_ammonia2.setStyleSheet(StyleSheet.normallabel_whitebg)
        ui.label_lux2.setText(str(float(SENSOR.LUX_list[-1])))
        if SENSOR.LUX_list[-1] > SETTINGS.INLUX['to'] or SENSOR.LUX_list[-1] < SETTINGS.INLUX['from']:
            ui.label_lux2.setStyleSheet(StyleSheet.normallabel_whitebg + StyleSheet.abnormaltext)
        else :
            ui.label_lux2.setStyleSheet(StyleSheet.normallabel_whitebg)
        if ui.stackedWidget.currentIndex() == 4:
            self.updateAirConditionPlot()

    @PyQt5.QtCore.pyqtSlot(int, bool)
    def updateBATHPlot(self, graph, new= True):
        if new:
            if self.radioButton_list[0][graph].isChecked() :
                self.bathgraph_list[graph].clear()
                time_list = [ '' if i%6 !=0 else bathDef_list[graph].DateTime_list[-i] for i in range(1,49)]
                stringaxis = pg.AxisItem(orientation='bottom')
                stringaxis.setTicks([dict(enumerate(time_list)).items()])
                stringaxis.setTickSpacing(5,5)
                stringaxis.setStyle(tickTextHeight=5)
                TMPgraph = self.bathgraph_list[graph].addPlot(row = 0, col = 0, rowspan = 1,title = '',axisItems = {'bottom': stringaxis})
                TMPgraph.getAxis('bottom').tickFont = self.font11
                TMPgraph.getAxis('left').tickFont = self.font11
                #TMPgraph.showGrid(True, True, 1)
                TMPgraph.getViewBox().setBackgroundColor(color=(0,0,0,190))
                DOgraph = self.bathgraph_list[graph].addPlot(row =1, col = 0, rowspan = 1,title = ' ',axisItems = {'bottom': stringaxis})
                DOgraph.getAxis('left').tickFont = self.font11
                DOgraph.getViewBox().setBackgroundColor(color=(0,0,0,190))
                PHgraph = self.bathgraph_list[graph].addPlot(row =2, col = 0, rowspan = 1,title = ' ',axisItems = {'bottom': stringaxis})
                PHgraph.getAxis('left').tickFont = self.font11
                PHgraph.getViewBox().setBackgroundColor(color=(0,0,0,190))
                TMPgraph.plot(bathDef_list[graph].TMP_list[-48:], pen=pg.mkPen(color=(245,183,0), width=3), symbol=('o'), \
                                                                symbolSize=4, symbolPen = pg.mkPen(color=(245,183,0), width =1),symbolBrush=(255,223,127))
                DOgraph.plot(bathDef_list[graph].DO_list[-48:], pen=pg.mkPen(color=(137,252,0), width=3), symbol=('o'), \
                                                                symbolSize=4, symbolPen = pg.mkPen(color=(137,252,0), width =1),symbolBrush=(200,255,134))
                PHgraph.plot(bathDef_list[graph].PH_list[-48:], pen=pg.mkPen(color=(0,220,200), width=3), symbol=('o'), \
                                                                symbolSize=4, symbolPen = pg.mkPen(color=(0,220,200), width =1),symbolBrush=(122,255,243))
        else:
            if self.radioButton_list[1][graph].isChecked():
                self.dictionary = bathDef_list[graph].WeekData_dict
            elif self.radioButton_list[2][graph].isChecked():
                self.dictionary = bathDef_list[graph].MonthData_dict
            time_list = ['' if i%24 !=0 else self.dictionary['TIME'][-i] for i in range(len(self.dictionary['TIME']))]
            self.bathgraph_list[graph].clear()
            stringaxis = pg.AxisItem(orientation='bottom')
            stringaxis.setTicks([dict(enumerate(time_list)).items()])
            stringaxis.setTickSpacing(5,5)
            #stringaxis.setStyle(autoExpandTextSpace = True, tickTextHeight=100)
            TMPgraph = self.bathgraph_list[graph].addPlot(row = 0, col = 0, rowspan = 1, title = '수온',axisItems = {'bottom': stringaxis})
            TMPgraph.getAxis('bottom').tickFont = self.font10
            TMPgraph.getAxis('left').tickFont = self.font11
            TMPgraph.getViewBox().setBackgroundColor(color=(0,0,0,200))
            DOgraph = self.bathgraph_list[graph].addPlot(row =1, col = 0, rowspan = 1, title = 'DO',axisItems = {'bottom': stringaxis})
            DOgraph.getAxis('left').tickFont = self.font11
            DOgraph.getViewBox().setBackgroundColor(color=(0,0,0,200))
            PHgraph = self.bathgraph_list[graph].addPlot(row =2, col = 0, rowspan = 1, title = 'pH',axisItems = {'bottom': stringaxis})
            PHgraph.getAxis('left').tickFont = self.font11
            PHgraph.getViewBox().setBackgroundColor(color=(0,0,0,200))
            TMPgraph.plot(self.dictionary['TMP'][:48], pen=pg.mkPen(color=(25,255,55), width=3), symbol=('o'), \
                                                                symbolSize=5, symbolPen = pg.mkPen(color=(128, 255, 145), width =1),symbolBrush=(255,255,255))
            DOgraph.plot(self.dictionary['DO'][:48], pen=pg.mkPen(color=(25,255,55), width=3), symbol=('o'), \
                                                                symbolSize=5, symbolPen = pg.mkPen(color=(128, 255, 145), width =1),symbolBrush=(255,255,255))
            PHgraph.plot(self.dictionary['PH'][:48],pen=pg.mkPen(color=(25,255,55), width=3), symbol=('o'), \
                                                                symbolSize=5, symbolPen = pg.mkPen(color=(128, 255, 145), width =1),symbolBrush=(255,255,255))
    
    def updateTMPPlot(self):
        time_list = ['' if i%6 !=0 else BATH1.DateTime_list[-i] for i in range(1,49)]
        ui.graphicsView_tmpgraph1.clear()
        stringaxis = pg.AxisItem(orientation='bottom')
        stringaxis.setTicks([dict(enumerate(time_list)).items()]) 
        tmpgraph = ui.graphicsView_tmpgraph1.addPlot(title = 'TMP', axisItems = {'bottom' : stringaxis})
        tmpgraph.getAxis('bottom').tickFont = self.font10
        tmpgraph.getAxis('left').tickFont = self.font11
        tmpgraph.getViewBox().setBackgroundColor(color=(0,0,0,200))
        tmpgraph.getViewBox().setBackgroundColor(color=(0,0,0,200))
        for i,BATH in enumerate([BATH1, BATH2, BATH3, BATH4]):
            tmpgraph.plot(BATH.PH_list[-48:], pen=pg.mkPen(color=StyleSheet.lineColor[i], width=3))#, symbol=('o'), \
                   # symbolSize=4, symbolPen = pg.mkPen(color=StyleSheet.symbolOutlineColor[i], width =2),symbolBrush=(255,255,255))
            tmpgraph.addItem(pg.InfiniteLine(SETTINGS.BATH_dict['BATH'+str(i+1)]['TMP']['from'],angle=0, 
                            movable=False,pen=pg.mkPen(color=StyleSheet.dotLineColor[i], width=2, style=QtCore.Qt.DotLine)))
            tmpgraph.addItem(pg.InfiniteLine(SETTINGS.BATH_dict['BATH'+str(i+1)]['TMP']['to'],angle=0,
                            movable=False,pen=pg.mkPen(color=StyleSheet.dotLineColor[i], width=2, style= QtCore.Qt.DotLine)))

    def updateDOPlot(self):
        time_list = ['' if i%6 !=0 else BATH1.DateTime_list[-i] for i in range(1,49)]
        ui.graphicsView_dograph1.clear()
        stringaxis = pg.AxisItem(orientation='bottom')
        stringaxis.setTicks([dict(enumerate(time_list)).items()]) 
        dograph = ui.graphicsView_dograph1.addPlot(title = 'DO', axisItems = {'bottom' : stringaxis})
        dograph.getAxis('left').tickFont = self.font11
        dograph.getAxis('bottom').tickFont = self.font10
        dograph.getViewBox().setBackgroundColor(color=(0,0,0,200))
        for i,BATH in enumerate([BATH1, BATH2, BATH3, BATH4]):
            dograph.plot(BATH.DO_list[-48:], pen=pg.mkPen(color=StyleSheet.lineColor[i], width=3))
            dograph.addItem(pg.InfiniteLine(SETTINGS.BATH_dict['BATH'+str(i+1)]['DO']['from'],angle=0, 
                            movable=False,pen=pg.mkPen(color=StyleSheet.dotLineColor[i], width=2, style=QtCore.Qt.DotLine)))
            dograph.addItem(pg.InfiniteLine(SETTINGS.BATH_dict['BATH'+str(i+1)]['DO']['to'],angle=0,
                            movable=False,pen=pg.mkPen(color=StyleSheet.dotLineColor[i], width=2, style= QtCore.Qt.DotLine)))

    def updatePHPlot(self):
        time_list = ['' if i%6 !=0 else BATH1.DateTime_list[-i] for i in range(1,49)]
        ui.graphicsView_phgraph1.clear()
        stringaxis = pg.AxisItem(orientation='bottom')
        stringaxis.setTicks([dict(enumerate(time_list)).items()]) 
        phgraph = ui.graphicsView_phgraph1.addPlot(title = 'PH', axisItems = {'bottom' : stringaxis})
        phgraph.getAxis('left').tickFont = self.font11
        phgraph.getAxis('left').setRange(0,15)
        phgraph.getAxis('bottom').tickFont = self.font10
        phgraph.getViewBox().setBackgroundColor(color=(0,0,0,200))
        for i,BATH in enumerate([BATH1, BATH2, BATH3, BATH4]):
            phgraph.plot(BATH.PH_list[-48:], pen=pg.mkPen(color=StyleSheet.lineColor[i], width=3))
            phgraph.addItem(pg.InfiniteLine(SETTINGS.BATH_dict['BATH'+str(i+1)]['PH']['from'],angle=0, 
                            movable=False,pen=pg.mkPen(color=StyleSheet.dotLineColor[i], width=2, style=QtCore.Qt.DotLine)))
            phgraph.addItem(pg.InfiniteLine(SETTINGS.BATH_dict['BATH'+str(i+1)]['PH']['to'],angle=0,
                            movable=False,pen=pg.mkPen(color=StyleSheet.dotLineColor[i], width=2, style= QtCore.Qt.DotLine)))
            
    @PyQt5.QtCore.pyqtSlot(bool, int)
    def updateAirConditionPlot(self, new = True, graph = 0):
        if new :
            if self.radioButton_list[0][4].isChecked():
                time_list = ['' if i%6 !=0 else SENSOR.SENSORS_DateTime_list[-i] for i in range(49)]
                ui.graphicsView_aircondition1.clear()
                stringaxis = pg.AxisItem(orientation = 'bottom')
                stringaxis.setTicks([dict(enumerate(time_list)).items()])
                graph1 = ui.graphicsView_aircondition1.addPlot(axisItems = {'bottom':stringaxis})
                graph1.getAxis('bottom').tickFont = self.font10
                graph1.getAxis('left').tickFont = self.font11
                graph1.getViewBox().setBackgroundColor(color=(0,0,0,200))
                if ui.checkBox_outtmp.isChecked():
                    graph1.plot(SENSOR.OUTTMP_list[-48:],pen=pg.mkPen(color=(245,183,0), width=3))
                if ui.checkBox_intmp.isChecked():
                    graph1.plot(SENSOR.INTMP_list[-48:],pen=pg.mkPen(color=(147,0,250), width=3))
                if ui.checkBox_inhumid.isChecked():
                    graph1.plot(SENSOR.INHUMID_list[-48:],pen=pg.mkPen(color=(0,220,200), width=3))
                if ui.checkBox_lux.isChecked():
                    graph1.plot(SENSOR.LUX_list[-48:],pen=pg.mkPen(color=(137,252,0), width=3))
            if self.radioButton_list[0][5].isChecked():
                time_list = ['' if i%6 !=0 else SENSOR.SENSORS_DateTime_list[-i] for i in range(49)]
                ui.graphicsView_aircondition2.clear()
                stringaxis = pg.AxisItem(orientation = 'bottom')
                stringaxis.setTicks([dict(enumerate(time_list)).items()])
                graph2 = ui.graphicsView_aircondition2.addPlot(axisItems = {'bottom':stringaxis})
                graph2.getAxis('bottom').tickFont = self.font10
                graph2.getAxis('left').tickFont = self.font11
                graph2.getViewBox().setBackgroundColor(color=(0,0,0,200))
                if ui.checkBox_co2.isChecked():
                    graph2.plot(SENSOR.CO2_list[-48:],pen=pg.mkPen(color=(245,183,0), width=3))
                if ui.checkBox_ammonia.isChecked():
                    graph2.plot(SENSOR.AMMONIA_list[-48:],pen=pg.mkPen(color=(137,252,0), width=3))
        else:
            if graph == 1:
                if self.radioButton_list[1][4].isChecked():
                    self.dictionary = SENSOR.WeekData_dict
                elif self.radioButton_list[2][4].isChecked():
                    self.dictionary = SENSOR.MonthData_dict
                time_list = ['' if i%24 !=0 else self.dictionary['TIME_sensors'][-i] for i in range(len(self.dictionary['TIME_sensors']))]
                stringaxis = pg.AxisItem(orientation = 'bottom')
                stringaxis.setTicks([dict(enumerate(time_list)).items()])
                ui.graphicsView_aircondition1.clear()
                graph1 = ui.graphicsView_aircondition1.addPlot(axisItems = {'bottom':stringaxis})
                graph1.getAxis('bottom').tickFont = self.font10
                graph1.getAxis('left').tickFont = self.font11
                graph1.getViewBox().setBackgroundColor(color=(0,0,0,200))
                if ui.checkBox_outtmp.isChecked():
                    graph1.plot(self.dictionary['OUTTMP'],pen=pg.mkPen(color=(245,183,0), width=3))
                if ui.checkBox_intmp.isChecked():
                    graph1.plot(self.dictionary['INTMP'],pen=pg.mkPen(color=(147,0,250), width=3))
                if ui.checkBox_inhumid.isChecked():
                    graph1.plot(self.dictionary['INHUMID'],pen=pg.mkPen(color=(0,220,200), width=3))
                if ui.checkBox_lux.isChecked():
                    graph1.plot(self.dictionary['LUX'],pen=pg.mkPen(color=(137,252,0), width=3))
            elif graph == 2:
                if self.radioButton_list[1][5].isChecked():
                    self.dictionary = SENSOR.WeekData_dict
                elif self.radioButton_list[2][5].isChecked():
                    self.dictionary = SENSOR.MonthData_dict
                time_list = ['' if i%24 !=0 else self.dictionary['TIME_sensors'][-i] for i in range(len(self.dictionary['TIME_sensors']))]
                stringaxis = pg.AxisItem(orientation = 'bottom')
                stringaxis.setTicks([dict(enumerate(time_list)).items()])
                ui.graphicsView_aircondition2.clear()
                graph2 = ui.graphicsView_aircondition2.addPlot(axisItems = {'bottom':stringaxis})
                graph2.getAxis('bottom').tickFont = self.font10
                graph2.getAxis('left').tickFont = self.font11
                graph2.getViewBox().setBackgroundColor(color = (0,0,0,200))
                if ui.checkBox_co2.isChecked():
                    graph2.plot(self.dictionary['CO2'],pen=pg.mkPen(color=(245,183,0), width=3))
                    # pen=pg.mkPen(color=(245,183,0), width=3), symbol=('o'), \
                    #         symbolSize=4, symbolPen = pg.mkPen(color=(230,,25), width =1),symbolBrush=(255,255,255))
                if ui.checkBox_ammonia.isChecked():
                    graph2.plot(self.dictionary['AMMONIA'],pen=pg.mkPen(color=(137,252,0), width=3))
            
    def updateSettings(self, pushButton_clicked = False, applyall_clicked = False, saveall_clicked = False,sensor='None'):
        if self.INITIALIZED_dict['settings'] == False:
            with open ('config.json', 'r') as jsonFile:
                settingsData = json.load(jsonFile)["SETTINGS"]
                for index in range(1,5):
                    SETTINGS.BATH_dict['BATH'+str(index)]['TMP']['from'] = settingsData["BATH"+str(index)]["TMP"]["from"]
                    SETTINGS.BATH_dict['BATH'+str(index)]['TMP']['to'] = settingsData["BATH"+str(index)]["TMP"]["to"]
                    SETTINGS.BATH_dict['BATH'+str(index)]['DO']['from'] = settingsData["BATH"+str(index)]["DO"]["from"]
                    SETTINGS.BATH_dict['BATH'+str(index)]['DO']['to'] = settingsData["BATH"+str(index)]["DO"]["to"]
                    SETTINGS.BATH_dict['BATH'+str(index)]['PH']['from'] = settingsData["BATH"+str(index)]["PH"]["from"]
                    SETTINGS.BATH_dict['BATH'+str(index)]['PH']['to'] = settingsData["BATH"+str(index)]["PH"]["to"]
                    SETTINGS.BATH_dict['BATH'+str(index)]['check'] = settingsData["BATH"+str(index)]["check"]
                for k,v in {"INTMP":SETTINGS.INTMP, "CO2":SETTINGS.CO2, "INLUX":SETTINGS.INLUX,
                    "EC":SETTINGS.EC, "INHUMID":SETTINGS.INHUMID, "AMMONIA":SETTINGS.AMMONIA}.items():
                    v['from'] = settingsData[k]["from"]
                    v['to'] = settingsData[k]['to']
                SETTINGS.ELECTRON['delay'] = settingsData["ELECTRON"]["delay"]
                SETTINGS.ELECTRON['month'] = settingsData["ELECTRON"]["month"]
                SETTINGS.ELECTRON['blackout'] = settingsData["ELECTRON"]["blackout"]
                SETTINGS.FREQ1 = settingsData["FREQ1"]
                SETTINGS.UNIT1 = settingsData["UNIT1"]
                SETTINGS.FREQ2 = settingsData["FREQ2"]
                SETTINGS.UNIT2 = settingsData["UNIT2"]
                SETTINGS.IP = settingsData["IP"]
                SETTINGS.PORT = settingsData['PORT']
            self.INITIALIZED_dict['settings'] = True
        if pushButton_clicked:
            for i,lineEdit in enumerate([ui.lineEdit_ip1, ui.lineEdit_ip2, ui.lineEdit_ip3, ui.lineEdit_ip4]):
                lineEdit.setText(SETTINGS.IP.split('.')[i])
            ui.lineEdit_port.setText(SETTINGS.PORT)
            ui.spinBox_sensorfreq1.setValue(int(SETTINGS.FREQ1))
            ui.spinBox_sensorfreq2.setValue(int(SETTINGS.FREQ2))
            classify = {'s':0, 'm':1, 'h':2}
            unit1 = classify[SETTINGS.UNIT1]
            unit2 = classify[SETTINGS.UNIT2]
            ui.comboBox_sensorunits1.setCurrentIndex(unit1)
            ui.comboBox_sensorunits2.setCurrentIndex(unit2)
            for index in range(4):
                self.bathSpinBox_list[index][0].setValue(SETTINGS.BATH_dict['BATH'+str(index+1)]['TMP']['from'])
                self.bathSpinBox_list[index][1].setValue(SETTINGS.BATH_dict['BATH'+str(index+1)]['TMP']['to'])
                self.bathSpinBox_list[index][2].setValue(SETTINGS.BATH_dict['BATH'+str(index+1)]['DO']['from'])
                self.bathSpinBox_list[index][3].setValue(SETTINGS.BATH_dict['BATH'+str(index+1)]['DO']['to'])
                self.bathSpinBox_list[index][4].setValue(SETTINGS.BATH_dict['BATH'+str(index+1)]['PH']['from'])
                self.bathSpinBox_list[index][5].setValue(SETTINGS.BATH_dict['BATH'+str(index+1)]['PH']['to'])
            ui.doubleSpinBox_intmp1.setValue(SETTINGS.INTMP['from'])
            ui.doubleSpinBox_intmp2.setValue(SETTINGS.INTMP['to'])
            ui.doubleSpinBox_co21.setValue(SETTINGS.CO2['from'])
            ui.doubleSpinBox_co22.setValue(SETTINGS.CO2['to'])
            ui.doubleSpinBox_lux1.setValue(SETTINGS.INLUX['from'])
            ui.doubleSpinBox_lux2.setValue(SETTINGS.INLUX['to'])
            ui.doubleSpinBox_ec1.setValue(SETTINGS.EC['from'])
            ui.doubleSpinBox_ec2.setValue(SETTINGS.EC['to'])
            ui.doubleSpinBox_inhumid1.setValue(SETTINGS.INHUMID['from'])
            ui.doubleSpinBox_inhumid2.setValue(SETTINGS.INHUMID['to'])
            ui.doubleSpinBox_ammonia1.setValue(SETTINGS.AMMONIA['from'])
            ui.doubleSpinBox_ammonia2.setValue(SETTINGS.AMMONIA['to'])
            ui.checkBox_dayelecalert.setCheckState(2) if SETTINGS.ELECTRON['delay'] == 'O' else 'X'
            ui.checkBox_monthelecalert.setCheckState(2) if SETTINGS.ELECTRON['month'] == 'O' else 'X'
            ui.checkBox_blackoutalert.setCheckState(2) if SETTINGS.ELECTRON['blackout'] == 'O' else 'X'
            #Qt.Unchecked 0 Qt.Checked 2  
            for i in range(8):
                self.bathcheckbox_list[i].setCheckState(2 if SETTINGS.BATH_dict['BATH'+str(i+1)]['check'] == 'O' else 0)
        elif applyall_clicked:
            index = ui.tabWidget_2.currentIndex()
            for i in range(4):
                for j in range(6):
                    self.bathSpinBox_list[i][j].setValue(self.bathSpinBox_list[index][j].value())
        elif saveall_clicked:
            for index in range(4):
                SETTINGS.BATH_dict['BATH'+str(index+1)]['TMP']['from'] = self.bathSpinBox_list[index][0].value()
                SETTINGS.BATH_dict['BATH'+str(index+1)]['TMP']['to'] = self.bathSpinBox_list[index][1].value()
                SETTINGS.BATH_dict['BATH'+str(index+1)]['DO']['from'] = self.bathSpinBox_list[index][2].value()
                SETTINGS.BATH_dict['BATH'+str(index+1)]['DO']['to'] = self.bathSpinBox_list[index][3].value()
                SETTINGS.BATH_dict['BATH'+str(index+1)]['PH']['from'] = self.bathSpinBox_list[index][4].value()
                SETTINGS.BATH_dict['BATH'+str(index+1)]['PH']['to'] = self.bathSpinBox_list[index][5].value()
        elif sensor == 'sensor1':
            if ui.comboBox_sensorunits1.currentText() == '초':
                SETTINGS.FREQ1 = ui.spinBox_sensorfreq1.value()
                SETTINGS.UNIT1 = 's'
            elif ui.comboBox_sensorunits1.currentText() == '분':
                SETTINGS.FREQ1 = ui.spinBox_sensorfreq1.value()
                SETTINGS.UNIT1 = 'm'
            elif ui.comboBox_sensorunits1.currentText() == '시':
                SETTINGS.FREQ1 = ui.spinBox_sensorfreq1.value()
                SETTINGS.UNIT1 = 'h'
        elif sensor == 'sensor2':
            print(ui.comboBox_sensorunits2.currentText())
            if ui.comboBox_sensorunits2.currentText() == '초':
                SETTINGS.FREQ2 = ui.spinBox_sensorfreq2.value()
                SETTINGS.UNIT2 = 's'
            elif ui.comboBox_sensorunits2.currentText() == '분':
                SETTINGS.FREQ2 = ui.spinBox_sensorfreq2.value()
                SETTINGS.UNIT2 = 'm'
            elif ui.comboBox_sensorunits2.currentText() == '시':
                SETTINGS.FREQ2 = ui.spinBox_sensorfreq2.value()
                SETTINGS.UNIT2 = 'h'
        elif sensor == 'server':
            SETTINGS.IP = '.'.join([ui.lineEdit_ip1.text(), ui.lineEdit_ip2.text(),ui.lineEdit_ip3.text(),ui.lineEdit_ip4.text()])
        elif sensor == 'intmp':
            SETTINGS.INTMP['from']= ui.doubleSpinBox_intmp1.value()
            SETTINGS.INTMP['to'] = ui.doubleSpinBox_intmp2.value()
        elif sensor == 'co2':
            SETTINGS.CO2['from']=ui.doubleSpinBox_co21.value()
            SETTINGS.CO2['to'] = ui.doubleSpinBox_co22.value()
        elif sensor == 'inlux':
            SETTINGS.INLUX['from'] = ui.doubleSpinBox_lux1.value()
            SETTINGS.INLUX['to'] = ui.doubleSpinBox_lux2.value()
        elif sensor == 'ec':
            SETTINGS.EC['from'] = ui.doubleSpinBox_ec1.value()
            SETTINGS.EC['to'] = ui.doubleSpinBox_ec2.value()
        elif sensor == 'inhumid':
            SETTINGS.INHUMID['from'] = ui.doubleSpinBox_inhumid1.value()
            SETTINGS.INHUMID['to'] = ui.doubleSpinBox_inhumid2.value()
        elif sensor == 'ammonia':
            SETTINGS.AMMONIA['from'] = ui.doubleSpinBox_ammonia1.value()
            SETTINGS.AMMONIA['to'] = ui.doubleSpinBox_ammonia2.value()
        elif sensor == 'electron':
            SETTINGS.ELECTRON['delay'] = 'O' if ui.checkBox_dayelecalert.isChecked() else 'X'
            SETTINGS.ELECTRON['month'] = 'O' if ui.checkBox_monthelecalert.isChecked() else 'X'
            SETTINGS.ELECTRON['blackout'] = 'O' if ui.checkBox_blackoutalert.isChecked() else 'X'
    
    def updateELEC(self):
        ui.label_elec1hour.setText(str(SENSOR.ELECTRON_dict['1hour']) if SENSOR.ELECTRON_dict['1hour'] != None else '0')
        ui.label_elec1day.setText(str(SENSOR.ELECTRON_dict['1day']) if SENSOR.ELECTRON_dict['1day'] != None else '0')
        ui.label_elec1week.setText(str(SENSOR.ELECTRON_dict['1week']) if SENSOR.ELECTRON_dict['1week'] != None else '0')
        ui.label_elec1month.setText(str(SENSOR.ELECTRON_dict['1month']) if SENSOR.ELECTRON_dict['1month'] != None else '0')
        if ui.stackedWidget.currentIndex() == 5:
            self.updateELECPlot(True)

    def updateELECPlot(self, new = True):
        if new :
            if self.radioButton_list[0][6].isChecked():
                time_list = ['' if i%6 != 0 else SENSOR.ELECTRON_DateTime_list[-i] for i in range(1,49)]
                ui.graphicsView_elecgraph.clear()
                stringaxis = pg.AxisItem(orientation = 'bottom')
                stringaxis.setTicks([dict(enumerate(time_list)).items()])
                elecgraph = ui.graphicsView_elecgraph.addPlot(title = '전력량',axisItems = {'bottom': stringaxis})
                elecgraph.getAxis('bottom').tickFont = self.font10
                elecgraph.getAxis('left').tickFont = self.font11
                elecgraph.getViewBox().setBackgroundColor(color=(0,0,0,200))
                elecgraph.plot(SENSOR.ELECTRON_list[-48:],pen=pg.mkPen(color=(25,255,55), width=3), symbol=('o'), \
                                symbolSize=4, symbolPen = pg.mkPen(color=(15,255,25), width =1),symbolBrush=(255,255,255))
        else:
            if self.radioButton_list[1][6].isChecked():
                self.dictionary = SENSOR.WeekData_dict
            elif self.radioButton_list[2][6].isChecked():
                self.dictionary = SENSOR.MonthData_dict
            ui.graphicsView_elecgraph.clear()
            time_list = ['' if i%6 != 0 else self.dictionary['TIME_electron'][-i] for i in range(len(self.dictionary['TIME_electron']))]
            stringaxis = pg.AxisItem(orientation = 'bottom')
            stringaxis.setTicks([dict(enumerate(time_list)).items()])
            elecgraph = ui.graphicsView_elecgraph.addPlot(title = '전력량',axisItems = {'bottom': stringaxis})
            elecgraph.getAxis('bottom').tickFont = self.font10
            elecgraph.getAxis('left').tickFont = self.font11
            elecgraph.getViewBox().setBackgroundColor(color=(0,0,0,200))
            elecgraph.plot(self.dictionary['ELECTRON'][-48:],pen=pg.mkPen(color=(25,255,55), width=3), symbol=('o'), \
                            symbolSize=4, symbolPen = pg.mkPen(color=(15,255,25), width =1),symbolBrush=(255,255,255))


def stopall(eventThread, valueUpdateThread, timeUpdateThread, uartCom, dbInsertManagerThread, dbFetchManagerThread):
    if uartCom.uart != None:
        uartCom.uart.loop.stop()
    if eventThread.isRunning():
        eventThread.terminate()
    if valueUpdateThread.isRunning():
        valueUpdateThread.terminate()
    if timeUpdateThread.isRunning():
        timeUpdateThread.terminate()
    #dbInsertManagerThread.disconnect()
    #dbFetchManagerThread.disconnect()
    print('saving data')
    with open ('config.json', 'r') as jsonFile:
        data = json.load(jsonFile)
        settingsData = data['SETTINGS']
        actuatordata = data["ACTUATOR"]
        for i, bath in enumerate(["BATH1", "BATH2", "BATH3", "BATH4"]):
            data[bath]["PUMP"] = bathDef_list[i].PUMP
            data[bath]["HEATER"] = bathDef_list[i].HEATER
        actuatordata["AIR"]["power"] = ACTUATOR.AIR['power']
        actuatordata["WIND"]["power"] = ACTUATOR.WIND['power']
        actuatordata["LED"]["power"] = ACTUATOR.LED['power']
        actuatordata["UV"]["power"] = ACTUATOR.UV['power']
        for index in range(1,5):
            settingsData["BATH"+str(index)]["TMP"]["from"] = SETTINGS.BATH_dict['BATH'+str(index)]['TMP']['from']
            settingsData["BATH"+str(index)]["TMP"]["to"] = SETTINGS.BATH_dict['BATH'+str(index)]['TMP']['to']
            settingsData["BATH"+str(index)]["DO"]["from"] = SETTINGS.BATH_dict['BATH'+str(index)]['DO']['from'] 
            settingsData["BATH"+str(index)]["DO"]["to"] = SETTINGS.BATH_dict['BATH'+str(index)]['DO']['to']
            settingsData["BATH"+str(index)]["PH"]["from"] = SETTINGS.BATH_dict['BATH'+str(index)]['PH']['from'] 
            settingsData["BATH"+str(index)]["PH"]["to"] = SETTINGS.BATH_dict['BATH'+str(index)]['PH']['to'] 
            settingsData["BATH"+str(index)]["check"] = SETTINGS.BATH_dict['BATH'+str(index)]['check']
        for k, v in {"INTMP":SETTINGS.INTMP, "CO2":SETTINGS.CO2, "INLUX":SETTINGS.INLUX,
                    "EC":SETTINGS.EC, "INHUMID":SETTINGS.INHUMID, "AMMONIA":SETTINGS.AMMONIA}.items(): 
            settingsData[k]["from"] = v['from']
            settingsData[k]['to'] = v['to']
        settingsData["ELECTRON"]["delay"] = SETTINGS.ELECTRON['delay'] 
        settingsData["ELECTRON"]["month"] = SETTINGS.ELECTRON['month']
        settingsData["ELECTRON"]["blackout"] = SETTINGS.ELECTRON['blackout'] 
        settingsData["FREQ1"] = SETTINGS.FREQ1
        settingsData["FREQ2"] = SETTINGS.FREQ2
        settingsData["UNIT1"] = SETTINGS.UNIT1
        settingsData["UNIT2"] = SETTINGS.UNIT2
    with open("config.json", "w") as jsonFile:
        json.dump(data, jsonFile, indent = 4)
    print("Closed all thread!")

if __name__ == '__main__':
    import sys
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    pg.setConfigOptions(antialias = True)
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    #MainWindow.showFullScreen()
    MainWindow.show()
    timeUpdateThread = TimeUpdateThread(ui)
    dbInsertManagerThread = DBInsertManager()
    eventThread = EventThread(ui)
    uartCom = UartCom(ui, eventThread, dbInsertManagerThread)
    valueUpdateThread = ValueUpdateThread(ui, uartCom, eventThread)
    dbFetchManagerThread = DBFetchManager(ui, eventThread)
    app.aboutToQuit.connect(lambda: stopall(eventThread, valueUpdateThread, timeUpdateThread, uartCom, dbInsertManagerThread, dbFetchManagerThread))
    sys.exit(app.exec_())