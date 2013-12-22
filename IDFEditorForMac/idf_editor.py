#!/usr/bin/env python
# quitter.py - provide a button to quit this "program"


import sys

from idf_doc import IdfDocument
from PySide.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide.QtGui import QMainWindow, QApplication,\
    QFileDialog, QStringListModel

from ui_idf_editor import Ui_MainWindow as Ui


class IdfEditorWindow(QMainWindow):
    def __init__(self, parent=None):
        super(IdfEditorWindow, self).__init__(parent)
        ui = Ui()
        self.ui = ui
        ui.setupUi(self)

        self.doc = IdfDocument()

        ui.listView.setModel(QStringListModel())
        ui.tableView.setModel(IdfObjectsTableModel(self.doc))

        # menu actions
        ui.actionOpen.triggered.connect(self.actionOpenFile)
        ui.actionSaveAs.triggered.connect(self.actionSaveFileAs)
        ui.actionShowClassesWithObjectsOnly.triggered.connect(self.actionShowClassesWithObjectsOnly)

        ui.listView.clicked.connect(self.actionClassClicked)

        self.showClassesWithObjectsOnly(False)
        self.selectClassAtIndex(0)

    # ------------------------------------------------------------------------
    # UI Actions
    # ------------------------------------------------------------------------

    def actionOpenFile(self):
        filetuple = QFileDialog.getOpenFileName(self,
                                                "Open File", ".",
                                                "*.idf\n*.expidf")
        self.openFile(filetuple[0])

    def actionSaveFileAs(self):
        filetuple = QFileDialog.getSaveFileName(self,
                                                "Save File", ".",
                                                "*.idf")
        self.saveFileAs(filetuple[0])

    def actionShowClassesWithObjectsOnly(self):
        print(self.ui.actionShowClassesWithObjectsOnly.isChecked())
        self.showClassesWithObjectsOnly(self.ui.actionShowClassesWithObjectsOnly.isChecked())

    def actionClassClicked(self, index):
        self.selectClassAtIndex(index.row())

    # ------------------------------------------------------------------------

    def openFile(self, filepath):
        self.doc.readFromFile(filepath)
        self.showClassesWithObjectsOnly(False)
        self.selectClassAtIndex(0)

    def saveFileAs(self, filepath):
        self.doc.writeToFile(filepath)

    def showClassesWithObjectsOnly(self, state):
        self.ui.actionShowClassesWithObjectsOnly.setChecked(state)
        if state:
            classes = self.doc.onlyClassesWithObjectsWithObjectCount()
        else:
            classes = self.doc.allClassesWithObjectCount()
        formatted_classes = []

        for classname, count in classes.items():
            formatted_classes.append("[{0:04d}] {1}".format(count, classname))
        model = QStringListModel(formatted_classes)
        self.ui.listView.setModel(model)

    def selectClassAtIndex(self, index):
        # select class in listview
        qindex = self.ui.listView.model().createIndex(index, 0)
        self.ui.listView.setCurrentIndex(qindex)
        # update tableview for selected class
        model = self.ui.tableView.model()
        model.classname = self.classes()[index]
        topleft = model.createIndex(0, 0)
        bottomright = model.createIndex(model.rowCount(0), model.columnCount(0))
        model.dataChanged.emit(topleft, bottomright)
        model.headerDataChanged.emit(Qt.Vertical, 0, model.rowCount(0))

    def selectClass(self, classname):
        try:
            self.selectClassAtIndex(self.classes().index(classname))
        except ValueError:
            pass

    def selectedClass(self):
        index = self.ui.listView.currentIndex().row()
        return self.classes()[index]

    def addNewObject(self):
        self.doc.addEmptyObject(self.selectedClass())

    def classes(self):
        if self.ui.actionShowClassesWithObjectsOnly.isChecked():
            return list(self.doc.onlyClassesWithObjectsWithObjectCount().keys())
        else:
            return list(self.doc.allClassesWithObjectCount().keys())


class IdfObjectsTableModel(QAbstractTableModel):

    def __init__(self, doc):
        super(IdfObjectsTableModel, self).__init__()
        self.doc = doc
        self.classname = ""

    def rowCount(self, parent=QModelIndex()):
        return len(self.doc.fieldsOfClass(self.classname))

    def columnCount(self, parent=QModelIndex()):
        return len(self.doc.objectsOfClass(self.classname))

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and self.classname:
            return self.doc.objectOfClassAtIndex(self.classname, index.column())[index.row()]

        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Vertical:
            return self.doc.fieldsOfClass(self.classname)[section]

        return None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = IdfEditorWindow()
    frame.show()
    app.exec_()
