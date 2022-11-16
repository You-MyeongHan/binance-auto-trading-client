import sys, os
from PyQt5.QtWidgets import QApplication,QWidget
from PyQt5.QtCore import Qt,QCoreApplication
from PyQt5 import uic
BASE_DIR=os.path.dirname(os.path.abspath(__file__))

class LoginWidget(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(BASE_DIR+"\\ui_resource\\login.ui", self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        
    def init_ui(self):
        self.close_window_btn.clicked.connect(QCoreApplication.instance().quit)
        self.minimize_window_btn.clicked.connect(self.showMinimized)
        self.login_btn.clicked.connect(self.login)

    def login(self):
        pass
    
if __name__=="__main__":
    app=QApplication(sys.argv)
    lw=LoginWidget()
    lw.show()
    exit(app.exec_())