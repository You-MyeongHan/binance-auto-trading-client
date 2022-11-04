import sys
from PyQt5 import uic
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget
import ccxt
import time
class OverViewWorker(QThread):
    dataSent = pyqtSignal(float, float, float)
    
    def __init__(self, ticker):
        super().__init__()
        self.ticker = ticker
        self.alive = True
        
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
        
    def run(self):
        while self.alive:
            data=self.binance.fetch_balance()
            price=self.binance.fetch_ticker(self.ticker)
            self.dataSent.emit(price['bid'],data['USDT']['free'],data['BTC']['used'])
            time.sleep(3)
        
    def close(self):
        self.alive = False
    
class BalanceWidget(QWidget):
    def __init__(self, parent=None, ticker="BTC/USDT"):
        super().__init__(parent)
        uic.loadUi("ui_resource/balance_price.ui", self)
        
        self.ticker = ticker
        self.bp = OverViewWorker(ticker)
        self.bp.dataSent.connect(self.update)
        self.bp.start()
    
    def update(self, price, balance, coin):
        self.label.setText(f"{price:,.2f} $")
        self.label_2.setText(f"{balance:,.2f} $")
        self.label_3.setText(f"{coin:,.2f} $")
        pass
    
    def closeEvent(self, event):
        self.bp.close()
        
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    bp = BalanceWidget()
    bp.show()
    exit(app.exec_())