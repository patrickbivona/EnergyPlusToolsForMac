#!/usr/bin/env python
# quitter.py - provide a button to quit this "program"
 
import sys
import os.path

from idf_doc import PyIdfDocument
 
from PySide.QtGui import QMainWindow, QApplication,\
     QFileDialog, QStringListModel
 
from ui_idf_editor import Ui_MainWindow as Ui
 
class IdfEditorWindow(QMainWindow):
    def __init__(self, parent=None):
        super(IdfEditorWindow, self).__init__(parent)
        ui = Ui()
        self.ui = ui
        ui.setupUi(self)

        ui.listView.setModel(QStringListModel())

        ui.actionOpen.triggered.connect(self.actionOpenFile)
        ui.actionSaveAs.triggered.connect(self.actionSaveFileAs)
        ui.actionShowClassesWithObjectsOnly.triggered.connect(self.actionShowClassesWithObjectsOnly)

        self.doc = PyIdfDocument()
        self.showClassesWithObjectsOnly(False)
      
    def actionOpenFile(self):
        filetuple = QFileDialog.getOpenFileName(self,\
                "Open File", ".", \
                "*.idf\n*.expidf")
        self.openFile(filetuple[0])

    def actionSaveFileAs(self):
        filetuple = QFileDialog.getSaveFileName(self,\
                "Save File", ".", \
                "*.idf")
        self.saveFileAs(filetuple[0])

    def actionShowClassesWithObjectsOnly(self):
        print(self.ui.actionShowClassesWithObjectsOnly.isChecked())
        self.showClassesWithObjectsOnly(self.ui.actionShowClassesWithObjectsOnly.isChecked())

    def openFile(self, filepath):
        self.doc.readFromFile(filepath)
        self.showClassesWithObjectsOnly(False)

    def saveFileAs(self, filepath):
        self.doc.writeToFile(filepath)

    def showClassesWithObjectsOnly(self, state):
        self.ui.actionShowClassesWithObjectsOnly.setChecked(state)
        if state == True:
            classes = self.doc.onlyClassesWithObjectsWithObjectCount()
        else:
            classes = self.doc.allClassesWithObjectCount()
        formatted_classes = []

        for classname, count in classes.items():
            formatted_classes.append("[{0:04d}] {1}".format(count, classname))
        model = QStringListModel(formatted_classes)
        self.ui.listView.setModel(model)

    def classes(self):
        formatted_classes = self.ui.listView.model().stringList()
        return [c[7:] for c in formatted_classes]

if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = IdfEditorWindow()
    frame.show()    
    app.exec_()
