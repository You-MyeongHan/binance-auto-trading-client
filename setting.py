import sys
import time
import pybithumb
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QTableWidgetItem, QProgressBar
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation



class SettingWorker(QThread):
    def __init__(self, ticker):
        super().__init__()
        self.alive = True

    def run(self):
        while self.alive:
            pass
    def close(self):
        self.alive=False

class SettingWidget(QWidget):
    def __init__(self, parent=None, ticker="BTC"):
        super().__init__(parent)
        uic.loadUi("ui_resource/setting_window.ui", self)
        self.ticker = ticker
        self.startButton.clicked.connect(self.clickStartButton)
        self.stopButton.clicked.connect(self.clickStopButton)
        self.predictButton.clicked.connect(self.clickPredictButton)
        self.buyButton.clicked.connect(self.clickBuyButton)
        self.sellButton.clicked.connect(self.clickSellButton)
        self.longButton.clicked.connect(self.clickLongButton)
        self.shortButton.clicked.connect(self.clickShortButton)

        self.sw = SettingWorker(self.ticker)
        self.sw.start()

    def closeEvent(self, event):
        self.sw.close()
    
    def clickStartButton(self):
        print("start trading")

    def clickStopButton(self):
        print("stop trading")
    
    def clickPredictButton(self):
        print("predict")

    def clickBuyButton(self):
        print("buy "+ self.ticker)
    
    def clickSellButton(self):
        print("sell" + self.ticker)

    def clickLongButton(self):
        print("set long postion")
    
    def clickShortButton(self):
        print("set short position")

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    sw = SettingWidget()
    sw.show()
    exit(app.exec_())