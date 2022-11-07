import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
class SettingDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui_resource/setting_dialog.ui", self)
        self.epoches=50
        self.model="LSTM"
        self.loss="MSE"
        self.activation="tanh"
        
    def onOKButtonClicked(self):
        self.accept()   
        
    def onCancelButtonClicked(self):
        self.reject()
        
    def showModal(self):
        return super().exec_()