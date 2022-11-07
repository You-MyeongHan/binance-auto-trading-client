import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget,QSizePolicy
from PyQt5.QtGui import QPainter
from PyQt5.QtChart import QLineSeries, QChart, QValueAxis, QDateTimeAxis
from PyQt5.QtCore import Qt, QDateTime
import time
import pandas as pd
import ccxt 
from PyQt5.QtCore import QThread, pyqtSignal

class chartWorker(QThread):
    dataSent = pyqtSignal(float)

    def __init__(self, ticker):
        super().__init__()
        self.ticker = ticker
        self.alive = True
        binance = ccxt.binance()
        btc_ohlcv = binance.fetch_ohlcv(ticker)

    def run(self):
        while self.alive:
            # data  = pybithumb.get_current_price(self.ticker)
            time.sleep(3600)
            # if data != None:
            #     self.dataSent.emit(data)

    def close(self):
        self.alive = False
        
class ChartWidget(QWidget):
    def __init__(self, parent=None, ticker="BTC/USDT"):
        super().__init__(parent)
        uic.loadUi("ui_resource/chart_window.ui", self)
        binance = ccxt.binance()
        ohlcv = binance.fetch_ohlcv(symbol=ticker, timeframe='1h')
        df = pd.DataFrame(ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        df.set_index('datetime', inplace=True)
        self.series1=QLineSeries()
        
        for index in df.index:
            close = df.loc[index, 'close']

            self.series1.append(index, close)
        
        self.chart=QChart()
        self.chart.legend().hide()
        self.chart.addSeries(self.series1)
        self.chart.setTitle("BTC/USDT")
        
        
        self.chart.setAnimationOptions(QChart.AllAnimations)
        
        axisX = QDateTimeAxis()
        axisX.setFormat("MM-dd hh:mm:ss")
        self.chart.addAxis(axisX, Qt.AlignBottom)
        self.series1.attachAxis(axisX)
        axisX.setTickCount(6)
        
        axisY = QValueAxis()
        axisY.setLabelFormat("%i $")
        self.chart.addAxis(axisY, Qt.AlignLeft)
        self.series1.attachAxis(axisY)
        self.chart.layout().setContentsMargins(0, 0, 0, 0)
        
        sizePolicy=QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHeightForWidth(self.chartView.sizePolicy().hasHeightForWidth())
        
        
        self.chartView.setChart(self.chart)
        self.chartView.setSizePolicy(sizePolicy)
        self.chartView.setRenderHint(QPainter.Antialiasing)
        self.chartView.chart().setTheme(QChart.ChartThemeDark)
        self.pw = chartWorker(ticker)
        # self.pw.dataSent.connect(self.appendData)
        self.pw.start()
        
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    cw = ChartWidget()
    cw.show()
    exit(app.exec_())