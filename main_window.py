import sys
import os
#sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal
from binance.client import Client
import datetime
from functools import partial
form_class = uic.loadUiType("ui_resource/mainWindow.ui")[0]

class MainWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("binance auto trading")
        
        self.init_ui()

    def init_ui(self):
        self.start_btn.clicked.connect(self.start)
        self.stop_btn.clicked.connect(self.stop)
        self.prediction_chart_btn.clicked.connect(self.predictChart)
        self.balance_chart_btn.clicked.connect(self.balanceChart)
        self.log_btn.clicked.connect(self.log)
        self.setting_btn.clicked.connect(self.setting)
    
    def start(self):
        print("start")
    
    def stop(self):
        print("stop")
        
    def predictChart(self):
        print("predictChart")
        
    def balanceChart(self):
        print("balanceChart")
        
    def log(self):
        print("log")
        
    def setting(self):
        print("setting")
    
    def close(self, event):
        self.alive = False
        
    
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    exit(app.exec_())

# class VolatilityWorker(QThread):
#     tradingSent = pyqtSignal(str, str, str)
    
#     def __init__(self, ticker, bithumb):
#         super().__init__()
#         self.ticker = ticker
#         self.bithumb = bithumb
#         self.alive = True

#     def run(self):
#         now = datetime.datetime.now()
#         mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(1)
#         ma5 = get_yesterday_ma5(self.ticker)
#         target_price = get_target_price(self.ticker)
#         wait_flag = False
#         print("target price :", target_price)
#         while self.alive:
#             try:
#                 now = datetime.datetime.now()
#                 if mid < now < mid + datetime.delta(seconds=10):
#                     target_price = get_target_price(self.ticker)
#                     mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(1)
#                     ma5 = get_yesterday_ma5(self.ticker)
#                     desc = sell_crypto_currency(self.bithumb, self.ticker)

#                     result = self.bithumb.get_order_completed(desc)
#                     timestamp = result['data']['order_date']
#                     dt = datetime.datetime.fromtimestamp( int(int(timestamp)/1000000) )
#                     tstring = dt.strftime("%Y/%m/%d %H:%M:%S")
#                     self.tradingSent.emit(tstring, "매도", result['data']['order_qty'])
#                     wait_flag = False

#                 if wait_flag == False:
#                     current_price = pybithumb.get_current_price(self.ticker)
#                     if (current_price > target_price) and (current_price > ma5):
#                         desc = buy_crypto_currency(self.bithumb, self.ticker)
#                         result = self.bithumb.get_order_completed(desc)
#                         timestamp = result['data']['order_date']
#                         dt = datetime.datetime.fromtimestamp( int(int(timestamp)/1000000) )
#                         tstring = dt.strftime("%Y/%m/%d %H:%M:%S")
#                         self.tradingSent.emit(tstring, "매수", result['data']['order_qty'])
#                         wait_flag = True
#             except:
#                 pass
#             time.sleep(1)

#     def close(self):
#         self.alive = False


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     mw = MainWindow()
#     mw.show()
#     exit(app.exec_())