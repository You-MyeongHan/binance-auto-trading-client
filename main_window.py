import sys
import os
import time
import ccxt
import csv
import requests
import pandas as pd
import asyncio
import aiohttp
import json
from datetime import datetime

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow,QApplication,QSizePolicy
from PyQt5.QtChart import QChart,QDateTimeAxis,QChartView,QLineSeries,QPieSeries
from PyQt5.QtCore import Qt, QDateTime, pyqtSignal, QThread,QCoreApplication,pyqtSlot
from PyQt5.QtGui import QPainter
from binance.client import Client
from functools import partial

from scheduler import SafeScheduler

form_class = uic.loadUiType("ui_resource/mainWindow.ui")[0]
SERVER_BASE='http://127.0.0.1:5000/api/'
# async def get_data():
#     async with aiohttp.ClientSession() as session:
#             async with session.get(SERVER_BASE+'predict') as response:
#                 print(response.json())

class MainWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.prediction_status=0 # 0:None, 1:buy, -1:sell
        self.init_ui()
        self.power_status=False
        self.now=datetime.now()
        self.fee_ratio=0.998
        self.body_frame.setStyleSheet(u"background-color: transparent;")
        
        with open("config.txt") as f:
            lines = f.readlines()
            self.api_key=lines[0].strip()
            self.sec_key=lines[1].strip()
            self.ticker = lines[2].strip()
            self.dataLen = int(lines[3].strip())

        self.binance = ccxt.binance(config={
            'apiKey': self.api_key,
            'secret': self.sec_key
        })

        self.show()

    def init_ui(self):
        self.setWindowTitle("binance auto trading")
        self.power_btn.clicked.connect(self.power)
        # self.line_btn.clicked.connect(self.lineChart)
        # self.balance_chart_btn.clicked.connect(self.balanceChart)
        self.setting_btn.clicked.connect(self.setting)
        self.close_window_btn.clicked.connect(self.close)
        self.minimize_window_btn.clicked.connect(self.minimize)

    # async def start(self):
    def power(self):
        self.power_status=not self.power_status
        if self.power_status:
            self.power_btn.setText("stop")
            self.sendLog("data training...", level="")
            
            
            data=self.get_predict_data()
            date=['1','2','3','4','5']
            price=[19700,18500,21000,16800,22000]
            self.current_price=self.binance.fetch_ticker(self.ticker)['bid']
            
            # date=datetime.fromtimestamp((self.get_predict_data()['date']+3600000)/1000)
            # date=datetime.strftime(date, "%Y-%m-%d %H:%m:%S")
            self.sendLog(message="Finish creating prediction dataset", level="info")
            
            for i in range(len(date)):
                message="date : "+ date[i] +", priece : "+str(price[i])
                self.sendLog(message, level="info")
                
            self.sendLog(message="Set Target price", level="info")
            balance=self.fetch_balance()
            if self.fee_ratio*self.current_price < min(price) and balance['USDT']['free'] > balance['BTC']['used'] :
                self.buy_market_order(price=self.current_price, amount=0.01)  
                self.sendLog(message="Buy order executed", level="info")
            elif self.fee_ratio*self.current_price > min(price) and balance['USDT']['free'] > balance['BTC']['used']:
                self.sell_market_order(price=self.current_price, amount=0.01) 
                self.sendLog(message="Sell order executed", level="info")
            else:
                self.sendLog(message="It is not a good time to set a position", level="info")
            # loop=asyncio.get_event_loop()
            # req=await loop.run_in_executor(None, requests.get, SERVER_BASE+'test')
            
            # response=requests.get(SERVER_BASE+'predict')
            # print(response.json()['data'])
            # if response.json()['message'] =="success":
            #     self.buy_limit_order(0.12, 100)
            # else:
            #     self.textEdit.append("No order position")
        else:
            self.power_btn.setText("start")
            self.sendLog("Stop predicting...", level="")


    def get_predict_data(self):
        response=requests.get(SERVER_BASE+'predict')
        print(response.json())
        
        return response.json()
        
    def sendLog(self, message: str, format=True, level="info"):
        if format:
            if level=="info":
                message="INFO - " + self.now.strftime('%m-%d %H:%M:%S') +"  " +message
            if level=="warning":
                message="WARNING - " + self.now.strftime('%m-%d %H:%M:%S')+"  " + message
            if level=="error":
                message="ERROR - " + self.now.strftime('%m-%d %H:%M:%S')+"  " + message
            if level=="debug":
                message="DEBUG - " + self.now.strftime('%m-%d %H:%M:%S')+"  " + message    
        self.textEdit.append(message)
        
    # def balanceChart(self):
    #     status = self.binance.fetch_balance()
    #     series=QPieSeries
    #     series.append("used balance", int(status['USDT']['used']))
    #     series.append("free balance", int(status['USDT']['free']))

    #     chart=QChart()
    #     chart.addSeries(series)
    #     chart.setAnimationOptions(QChart.SeriesAnimations)
    #     chart.setTitle(str(status['USDT']['total']))
    #     self.balance_chart_cont.addWidget(self.chart_view)
    #     self.frame_17.setStyleSheet(u"background-color:transparent;")
    #     self.stackedWidget.setCurrentIndex(3)

    #     message='total balance : '+str(status['USDT']['total'])+'\nused balance : '+str(status['USDT']['used'])+'\nfree balance : '+str(status['USDT']['free'])
    #     self.textEdit.append(message)
    #     self.show()
        
    def setting(self):
        print("setting")
    
    def close(self):
        self.alive = False
        self.close_window_btn.clicked.connect(QCoreApplication.instance().quit)

    def minimize(self):
        pass
        
    def fetch_coin_data(self, dataLen):
        ohlcv =self.binance.fetch_ohlcv(self.ticker, '1h', limit=dataLen)
        df = pd.DataFrame(ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
        df.set_index('datetime', inplace=True)
        return df

    def fetch_balance(self):
        return self.binance.fetch_balance()
    # order = client.create_order(
    #     symbol='BNBBTC',
    #     side=SIDE_BUY,
    #     type=ORDER_TYPE_LIMIT,
    #     timeInForce=TIME_IN_FORCE_GTC,
    #     quantity=100,
    #     price='0.00001')

    def buy_market_order(self, price, amount):
        try:
            order = self.binance.create_limit_buy_order(
                symbol=self.ticker, 
                price=price,
                amount=amount
            )
            self.textEdit.append("[BUY ORDER]\n"+order['datetime']+" - "+order['price']+" - "+ order['amount'])
        except Exception as e:
            print(e)
            self.sendLog('Maybe You do not have enough money or the amount of order size is too small',level='warning')
        

    def sell_market_order(self, price, amount):
        try:
            order = self.binance.create_limit_sell_order(
                symbol=self.ticker, 
                price=price,
                amount=amount
            )
            self.textEdit.append("[SELL ORDER]\n"+order['datetime']+" - "+order['price']+" - "+ order['amount'])
        except Exception as e:
            print(e)
            self.sendLog('Maybe You do not have enough money or the amount of order size is too small',level='warning')
        

    # @pyqtSlot(float)
    # def get_price_5minutes(self):
    #     if len(self.series1) == self.dataLen :
    #         self.series1.remove()
    #     sets = self.series1.sets()
    #     last_set = sets[-1] 
    #     self.series.remove(last_set)
    

# class ChartWorker(QThread):
#     dataSent = pyqtSignal(float)
    
#     def __init__(self):
#         super().__init__()
#         self.alive = True
#         self.binance = ccxt.binance()

#     def run(self):
#         pass
#         while self.alive:
#             df = self.binance.fetch_ticker("BTC/USDT")
#             self.dataSent.emit(df['open'],df['high'],df['low'],df['close'])
#             time.sleep(5) #5minutes    

    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()

    exit(app.exec_())