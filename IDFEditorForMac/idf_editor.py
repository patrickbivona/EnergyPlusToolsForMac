#!/usr/bin/env python
# quitter.py - provide a button to quit this "program"
 
import sys
 
from PySide.QtGui import QMainWindow, QPushButton, QApplication
 
from ui_idf_editor import Ui_MainWindow as Ui
 
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        ui = Ui()
        self.ui = ui
        ui.setupUi(self)
       
if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = MainWindow()
    frame.show()    
    app.exec_()
