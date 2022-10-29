import sys
import os
import time
import datetime
import ccxt
import csv

import pandas as pd

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow,QApplication
from PyQt5.QtChart import QChart,QDateTimeAxis,QCandlestickSet,QValueAxis,QCandlestickSeries,QChartView
from PyQt5.QtCore import Qt, QDateTime, pyqtSignal, QThread
from PyQt5.QtGui import QPainter
from binance.client import Client
from functools import partial

form_class = uic.loadUiType("ui_resource/mainWindow.ui")[0]

class MainWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_ui()
        
        self.binance=ccxt.binance()
        # self.config=[]
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

    def start(self):
        print("start")
    
    def stop(self):
        print("stop")
        
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
        
        self.show()
    
    def lineChart(self):
        pass
    
    def balanceChart(self):
        print("balanceChart")
        
    def log(self):
        print("log")
        
    def setting(self):
        print("setting")
    
    def close(self, event):
        self.alive = False
        
    def fetch_coin_data(self, dataLen):
        ohlcv =self.binance.fetch_ohlcv("BTC/USDT", '5m', limit=dataLen)
        df = pd.DataFrame(ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
        df.set_index('datetime', inplace=True)
        return df

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