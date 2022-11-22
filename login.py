import sys, os
from PyQt5.QtWidgets import QApplication,QWidget,QStackedWidget
from PyQt5.QtCore import Qt,QCoreApplication
from PyQt5 import uic
import pandas as pd
import requests
from main_window import *

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
SERVER_BASE='http://127.0.0.1:5000/api/'

class LoginWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(BASE_DIR+"\\ui_resource\\login.ui", self)
        self.init_ui()
        self.setWindowFlag(Qt.FramelessWindowHint)
        
    def init_ui(self):
        self.close_window_btn.clicked.connect(QCoreApplication.instance().quit)
        self.minimize_window_btn.clicked.connect(self.showMinimized)
        self.login_btn.clicked.connect(self.login)

    def login(self):
        id=self.id_line.text()
        password=self.pass_line.text()
        datas={'id':id, 'password':password}
        response=requests.post(SERVER_BASE+'login',data=datas)
        response=response.json()
        # userId=pd.read_json(response)
        self.close()
        
        mw=MainWindow()
        mw.show()
    
if __name__=="__main__":
    app=QApplication(sys.argv)
    lw=LoginWidget()
    lw.show()
    exit(app.exec_())