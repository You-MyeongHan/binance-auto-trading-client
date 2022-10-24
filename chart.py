from datetime import datetime
import sys
import time
import ccxt
import pandas as pd 

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter
from PyQt5.QtChart import QLineSeries, QChart, QValueAxis, QDateTimeAxis, QCandlestickSeries,QCandlestickSet, QChartView
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtCore import *
from pandas.core import frame

from PyQt5.QtCore import QThread, pyqtSignal

class ChartWorker(QThread):
    dataSent = pyqtSignal(frame.DataFrame)
    
    def __init__(self):
        super().__init__()
        self.alive = True

        with open("config.txt") as f:
            lines = f.readlines()
        #     apikey = lines[0].strip()
        #     seckey = lines[1].strip()
            self.ticker = lines[2].strip()
            self.dataLen = int(lines[3].strip())

    def run(self):
        while self.alive:
            time.sleep(300) #5minutes
            data=self.binance.fetch_ohlcv(self.ticker, '5m', limit=1)
            df = pd.DataFrame(data, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
            df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
            df.set_index('datetime', inplace=True)

            if df != None:
                self.dataSent.emit(df)

    def close(self):
        self.alive = False

class ChartWidget(QWidget):
    def __init__(self, parent=None, ticker="BTC/USDT"):
        super().__init__(parent)
        
        uic.loadUi("ui_resource/chart_window.ui", self)
        self.ticker = ticker
        self.dataLen = 500

        self.cw = ChartWorker()
        self.cw.dataSent.connect(self.appendData)
        self.cw.start()

        self.minute_cur = QDateTime.currentDateTime()   # current
        self.minute_pre = self.minute_cur.addSecs(-self.dataLen*5*60)  # 1 minute ago
        self.ticks = pd.Series(dtype='float64') 

        self.series = QCandlestickSeries()
        self.series.setIncreasingColor(Qt.red)
        self.series.setDecreasingColor(Qt.blue)    

        self.binance=ccxt.binance()
        self.ohlcv = self.binance.fetch_ohlcv(self.ticker, '5m', limit=self.dataLen)
        df = pd.DataFrame(self.ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
        df.set_index('datetime', inplace=True)

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
            self.series.append(elem)
        
        self.chart = QChart()
        self.chart.legend().hide()
        self.chart.addSeries(self.series)
        

        axis_x = QDateTimeAxis()
        axis_x.setFormat("hh:mm:ss")
        self.chart.addAxis(axis_x, Qt.AlignBottom)
        self.series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setLabelFormat("%i")
        self.chart.addAxis(axis_y, Qt.AlignLeft)
        self.series.attachAxis(axis_y)
        # axis_x.setTickCount(10) #

        print(open)
        print("check point1")

        self.chartView.setChart(self.chart)
        self.chartView.setRenderHint(QPainter.Antialiasing)
        
#===========================================================================

    @pyqtSlot(frame.DataFrame)
    def appendData(self, currPrice):
        dt = QDateTime.currentDateTime()
        self.statusBar().showMessage(dt.toString())
        self.ticks[dt] = currPrice

        # check whether minute changed
        #if dt.time().minute() != self.minute_cur.time().minute():


        sets = self.series.sets()
        last_set = sets[-1]                  

        open = last_set.open()
        high = last_set.high()
        low = last_set.low()
        close = last_set.close()
        ts1 = last_set.timestamp()
        self.series.remove(last_set)        # remove last set

        new_set = QCandlestickSet(open, high, low, close, ts1)
        self.series.append(new_set)

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    cw = ChartWidget()
    cw.show()
    exit(app.exec_())