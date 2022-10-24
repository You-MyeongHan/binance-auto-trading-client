import sys
import os
#sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QThread, pyqtSignal
from binance.client import Client
import datetime

form_class = uic.loadUiType("ui_resource/main_window.ui")[0]

class MainWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("binance auto trading")

        with open("config.txt") as f:
            lines = f.readlines()
            apikey = lines[0].strip()
            seckey = lines[1].strip()
            self.ticker = lines[1].strip()

    def closeEvent(self, event):
        self.chart_widget.closeEvent(event)
        self.widget_2.closeEvent(event)
        self.widget_3.closeEvent(event)

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