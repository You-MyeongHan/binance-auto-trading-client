import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow,QApplication,QSizePolicy,QDialog
from PyQt5.QtChart import QChart,QDateTimeAxis,QChartView,QLineSeries,QPieSeries
from PyQt5.QtCore import Qt, QDateTime, pyqtSignal, QThread,QCoreApplication,pyqtSlot
from PyQt5.QtGui import QPainter, QIcon
from binance.client import Client
from functools import partial

class SettingDialog(QDialog):
    def __inin__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("ui_resource/setting_dialog.ui", self)
        uic.show()
        self.epochs=50
        self.model="LSTM"
        self.loss="MSE"
        self.activation="tanh"
        self.init_ui()
        
    def init_ui(self):
        self.OK_btn.clicked.connect(self.pushButtonClicked)
        self.exec_()
        
    def pushButtonClicked(self):
        self.epochs = self.lineEdit.text()
        self.model = self.conboBox_3.text()
        self.loss=self.conboBox.text()
        self.activation=self.conboBox_2.text()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = SettingDialog()
    mw.show()
    exit(app.exec_())