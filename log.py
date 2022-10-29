import sys
import time
from PyQt5 import uic
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QTableWidgetItem, QProgressBar
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation

class LogWorker(QThread):
    def __init__(self, ticker):
        super().__init__()
        self.ticker = ticker
        self.alive = True

    def run(self):
        pass
    
    def close(self):
        self.alive=False

class LogWidget(QTextEdit):
    def __init__(self, parent=None, ticker="BTC"):
        super().__init__(parent)
        uic.loadUi("ui_resource/log_window.ui", self)
        self.ticker=ticker

        self.lw=LogWorker(self.ticker)
        #self.lw.dataSent.connect(self.updateData)
        self.lw.start()

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    lw = LogWidget()
    lw.show()
    exit(app.exec_())