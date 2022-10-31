import sys
import os
import time
import datetime
import ccxt
import csv
import requests
import pandas as pd
import asyncio

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow,QApplication,QSizePolicy
from PyQt5.QtChart import QChart,QDateTimeAxis,QCandlestickSet,QValueAxis,\
    QCandlestickSeries,QChartView,QLineSeries
from PyQt5.QtCore import Qt, QDateTime, pyqtSignal, QThread,QSize,QCoreApplication
from PyQt5.QtGui import QPainter
from binance.client import Client
from functools import partial

form_class = uic.loadUiType("ui_resource/mainWindow.ui")[0]
SERVER_BASE='http://127.0.0.1:5000/api/'

class MainWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.prediction_status=0 # 0:None, 1:buy, -1:sell
        self.init_ui()

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
        self.start_btn.clicked.connect(self.start)
        self.stop_btn.clicked.connect(self.stop)
        self.prediction_chart_btn.clicked.connect(self.predictChart)
        self.line_btn.clicked.connect(self.lineChart)
        self.balance_chart_btn.clicked.connect(self.balanceChart)
        self.log_btn.clicked.connect(self.log)
        self.setting_btn.clicked.connect(self.setting)
        self.close_window_btn.clicked.connect(self.close)
        self.minimize_window_btn.clicked.connect(self.minimize)

    # async def start(self):
    def start(self):
        self.textEdit.append("predicting...")
        # loop=asyncio.get_event_loop()
        # req=await loop.run_in_executor(None, requests.get, SERVER_BASE+'test')
        
        response=requests.get(SERVER_BASE+'test')
        if response.json()['message'] =="success":
            self.buy_limit_order(0.12, 100)
        else:
            self.textEdit.append("No order position")
    
    def stop(self):
        print("stop")

    def lineChart(self):
        self.series1=QLineSeries()
        
        rowCount=0
        df=self.fetch_coin_data(500)
        for index in df.index:
            if rowCount>0:
                self.series1.append(float(rowCount), df.loc[index, 'close'])
            
            rowCount+=1
        
        self.chart=QChart()
        self.chart.legend().hide()
        self.chart.addSeries(self.series1)
        self.chart.createDefaultAxes()
        self.chart.setTitle("BTC/USDT")
        
        self.chartView=QChartView(self.chart)
        self.chartView.setRenderHint(QPainter.Antialiasing)
        self.chart.setAnimationOptions(QChart.AllAnimations)
        self.chartView.chart().setTheme(QChart.ChartThemeDark)
        
        sizePolicy=QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHeightForWidth(self.chartView.sizePolicy().hasHeightForWidth())
        self.chartView.setSizePolicy(sizePolicy)
        self.chartView.setMinimumSize(QSize(0,300))
        
        self.line_chart_conf.addWidget(self.chartView)
        self.frame_20.setStyleSheet(u"background-color: transparent;")
        self.stackedWidget.setCurrentIndex(1)
        
    def predictChart(self):
        
        self.minute_cur = QDateTime.currentDateTime()   # current
        self.minute_pre = self.minute_cur.addSecs(-300)  # 5 minute ago
        self.ticks = pd.Series(dtype='float64')
        
        series = QCandlestickSeries()
        series.setIncreasingColor(Qt.red)
        series.setDecreasingColor(Qt.blue)
        
        df=self.fetch_coin_data(50)
        
        for index in df.index:
            open = df.loc[index, 'open']
            high = df.loc[index, 'high']
            low = df.loc[index, 'low']
            close = df.loc[index, 'close']

            format = "%Y-%m-%d %H:%M:%S"
            str_time = index.strftime(format)
            dt = QDateTime.fromString(str_time, "MM-dd hh:mm:ss")
            ts = dt.toMSecsSinceEpoch()
            
            elem = QCandlestickSet(open, high, low, close, ts)
            series.append(elem)
            
        chart = QChart()
        chart.legend().hide()
        chart.addSeries(series)
        chart.setAnimationOptions(QChart.SeriesAnimations)

        axis_x = QDateTimeAxis()
        axis_x.setFormat("hh:mm:ss")
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setLabelFormat("%i")
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)

        self.chart_view=QChartView(chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.prediction_chart_cont.addWidget(self.chart_view)
        self.frame_16.setStyleSheet(u"background-color:transparent;")
        self.stackedWidget.setCurrentIndex(2)
        self.show()
    
    def balanceChart(self):
        print("balanceChart")
        self.stackedWidget.setCurrentIndex(4)
        
    def log(self):
        # self.textEdit.append("==============================================log==============================================")
        self.stackedWidget.setCurrentIndex(3)
        
    def setting(self):
        print("setting")
    
    def close(self):
        self.alive = False
        self.close_window_btn.clicked.connect(QCoreApplication.instance().quit)

    def minimize(self):
        pass
        
    def fetch_coin_data(self, dataLen):
        ohlcv =self.binance.fetch_ohlcv(self.ticker, '5m', limit=dataLen)
        df = pd.DataFrame(ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
        df.set_index('datetime', inplace=True)
        return df

    # order = client.create_order(
    #     symbol='BNBBTC',
    #     side=SIDE_BUY,
    #     type=ORDER_TYPE_LIMIT,
    #     timeInForce=TIME_IN_FORCE_GTC,
    #     quantity=100,
    #     price='0.00001')

    def buy_market_order(self, price, amount=1):
        order = self.binance.create_limit_buy_order(
            symbol=self.ticker, 
            price=price,
            amount=amount
        )
        self.textEdit.append("[BUY ORDER]\n"+order['datetime']+" - "+order['price']+" - "+ order['amount'])

    def sell_market_order(self, price, amount=1):
        order = self.binance.create_limit_sell_order(
            symbol=self.ticker, 
            price=price,
            amount=amount
        )
        self.textEdit.append("[SELL ORDER]\n"+order['datetime']+" - "+order['price']+" - "+ order['amount'])



class ChartWorker(QThread):
    dataSent = pyqtSignal(float,float,float,float)
    
    def __init__(self):
        super().__init__()
        self.alive = True
        
        with open('sample_coin_data.csv') as data:
            csvReader=csv.reader(data, delimiter=',')
            
        
        # with open("config.txt") as f:
        #     lines = f.readlines()
        #     self.ticker = lines[2].strip()
        #     self.dataLen = int(lines[3].strip())
        # self.binance = ccxt.binance()

    def run(self):
        pass
        # while self.alive:
        #     df = self.binance.fetch_ticker("BTC/USDT")
        #     self.dataSent.emit(df['open'],df['high'],df['low'],df['close'])
        #     time.sleep(5) #5minutes    

    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    exit(app.exec_())