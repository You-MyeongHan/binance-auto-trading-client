import sys
from PyQt5 import uic
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget
import ccxt

class OverViewWorker(QThread):
    dataSent = pyqtSignal(float, float, float)
    
    def __init__(self, ticker):
        super().__init__()
        self.ticker = ticker
        self.alive = True
        
    def run(self):
        while self.alive:
            pass
        
    def close(self):
        self.alive = False
    
class BalanceWidget(QWidget):
    def __init__(self, parent=None, ticker="BTC/USDT"):
        super().__init__(parent)
        uic.loadUi("ui_resource/balance_price.ui", self)
        
        self.ticker = ticker
        self.bp = OverViewWorker(ticker)
        self.bp.dataSent.connect(self.dataSent)
    
    def dataSent(self, price, spot, coin):
        self.label.setText('20000$')
        self.label_2.setText("300$")
        self.label_3.setText("1.542BTC")
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