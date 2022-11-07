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
from PyQt5.QtWidgets import QMainWindow,QApplication,QSizePolicy,QDialog
from PyQt5.QtChart import QChart,QDateTimeAxis,QChartView,QLineSeries,QPieSeries
from PyQt5.QtCore import Qt, QDateTime, pyqtSignal, QThread,QCoreApplication,pyqtSlot
from PyQt5.QtGui import QPainter, QIcon
from binance.client import Client
from functools import partial

form_class = uic.loadUiType("ui_resource/mainWindow.ui")[0]
SERVER_BASE='http://127.0.0.1:5000/api/'

class PredictionWorker(QThread):
    dataSent=pyqtSignal(pd.Series,pd.Series)
    
    def __init__(self, ticker):
        super().__init__()
        self.ticker = ticker
        self.alive = True
    
    def run(self):
        data=self.get_predict_data()
        price=data['close']
        date=data['date']
        self.dataSent.emit(price, date)
        time.sleep(3600)
        
    def get_predict_data(self):
        response=requests.get(SERVER_BASE+'predict')
        response=response.json()
        data=pd.read_json(response)
        return data
    
    def close(self):
        self.alive = False

class MainWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.prediction_status=0 # 0:None, 1:buy, -1:sell
        self.init_ui()
        self.power_status=False
        self.now=datetime.now()
        self.buy_fee_ratio=1.002
        self.sell_fee_ratio=0.098
        
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

        def moveWindow(e):
            if self.isMaximized() == False:
                if e.buttons() == Qt.LeftButton:
                    self.move(self.pos() + e.globalPos() - self.clickPosition)
                    self.clickPosition = e.globalPos()
                    e.accept()
        self.header_frame.mouseMoveEvent=moveWindow
        
        self.show()

    def init_ui(self):
        self.setWindowTitle("binance auto trading")
        self.power_btn.clicked.connect(self.power)
        # self.line_btn.clicked.connect(self.lineChart)
        # self.balance_chart_btn.clicked.connect(self.balanceChart)
        self.close_window_btn.clicked.connect(QCoreApplication.instance().quit)
        self.restore_window_btn.clicked.connect(self.restore_or_maximize_window)
        self.minimize_window_btn.clicked.connect(self.showMinimized)
        self.setting_btn.clicked.connect(self.setting)
        
    # async def start(self):
    def mousePressEvent(self, event):
        self.clickPosition=event.globalPos()
        
    def power(self):
        self.power_status=not self.power_status
        if self.power_status:
            self.power_btn.setText("stop")
            self.sendLog("++++++++++++++++++++++++++++++++++++++++++START++++++++++++++++++++++++++++++++++++++++++", level="")
            self.sendLog("data training...", level="")
            
            self.pw=PredictionWorker(self.ticker)
            self.pw.dataSent.connect(self.auto_trading)
            self.pw.start()
        else:
            self.power_btn.setText("start")
            self.sendLog("++++++++++++++++++++++++++++++++++++++++++STOP+++++++++++++++++++++++++++++++++++++++++++", level="")
            self.pw.close()
        
    def auto_trading(self, price, date):
        self.current_price=self.binance.fetch_ticker(self.ticker)['bid']
        self.sendLog(message="Finish creating prediction dataset", level="info")
        for i in range(len(date)-10, len(date)):
            message="date : "+ str(date[i]) +", priece : "+str(price[i])
            self.sendLog(message, level="info")
            
        self.sendLog(message="Set Target price : "+str(min(price.tail(10))), level="info")
        balance=self.fetch_balance()
        buy_least_price=self.buy_fee_ratio*self.current_price
        sell_least_price=self.sell_fee_ratio*self.current_price

        if buy_least_price < min(price.tail(10)) and balance['USDT']['total'] > balance['BTC']['total']*self.current_price :
            self.buy_market_order(price=self.current_price, amount=0.01)
            self.sendLog(message="Buy order executed", level="info")
        elif sell_least_price >= min(price.tail(10)) and balance['USDT']['total'] < balance['BTC']['total']*self.current_price:
            self.sell_market_order(price=self.current_price, amount=0.01) 
            self.sendLog(message="Sell order executed", level="info")
        else:
            self.sendLog(message="It's not a good time to set a position", level="info")
        
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
        dialog=SettingDialog()
        dialog.exec_()
        self.epochs=dialog.epochs
        self.model=dialog.model
        self.loss=dialog.loss
        self.activation=dialog.activation

    def restore_or_maximize_window(self):
        if self.isFullScreen():
            self.showNormal()
            self.restore_window_btn.setIcon(QIcon(u":/icons/maximize-2.svg"))
        else:
            self.showFullScreen()
            self.restore_window_btn.setIcon(QIcon(u":/icons/minimize-2.svg"))
    
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
            self.sendLog('binance Account has insufficient balance for requested action.',level='warning')
        

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

class SettingDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        uic.loadUi("ui_resource/setting_dialog.ui", self)
        self.init_ui()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.epochs=50
        self.model="LSTM"
        self.loss="MSE"
        self.activation="tanh"
        
    def init_ui(self):
        self.OK_btn.clicked.connect(self.pushButtonClicked)
        self.cancel_btn.clicked.connect(self.close)
        
    def pushButtonClicked(self):
        self.epochs = self.lineEdit.text()
        self.model = self.comboBox_3.text()
        self.loss=self.comboBox.text()
        self.activation=self.comboBox_2.text()
        self.close()
    
    def close(self):
        self.reject()
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    exit(app.exec_())