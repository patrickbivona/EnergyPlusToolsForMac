#!/usr/bin/env python
# quitter.py - provide a button to quit this "program"


import sys
import os
import copy
from idf_doc import IdfDocument
from PyQt4.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt4.QtGui import QMainWindow, QApplication,\
    QFileDialog, QStringListModel

from ui_idf_editor import Ui_MainWindow as Ui


class IdfEditorWindow(QMainWindow):
    def __init__(self, parent=None):
        super(IdfEditorWindow, self).__init__(parent)
        ui = Ui()
        self.ui = ui
        ui.setupUi(self)

        self.doc = IdfDocument()
        self.currentfile = ''

        ui.listView.setModel(QStringListModel())
        ui.tableView.setModel(IdfObjectsTableModel(self.doc))

        # menu actions
        ui.actionOpen.triggered.connect(self.actionOpenFile)
        ui.actionSave.triggered.connect(self.actionSaveFile)
        ui.actionSaveAs.triggered.connect(self.actionSaveFileAs)
        ui.actionShowClassesWithObjectsOnly.triggered.connect(self.actionShowClassesWithObjectsOnly)

        ui.actionNewObject.triggered.connect(self.actionNewObject)
        ui.actionDuplicateObject.triggered.connect(self.actionDuplicateObject)
        ui.actionDeleteObject.triggered.connect(self.actionDeleteObject)
        ui.actionCopyObject.triggered.connect(self.copyObject)
        ui.actionPasteObject.triggered.connect(self.pasteObject)

        ui.listView.clicked.connect(self.actionClassClicked)

        self.showClassesWithObjectsOnly(False)
        self.selectClassAtIndex(0)

        self.ui.tableView.model().columnsInserted.connect(self.changedObjectCountToClass)
        self.ui.tableView.model().columnsRemoved.connect(self.changedObjectCountToClass)

        self.ui.tableView.selectionModel().selectionChanged.connect(self.objectSelectionChanged)
        QApplication.clipboard().dataChanged.connect(self.clipboardDataChanged)

    def objectSelectionChanged(self, selected, deselected):
        # this seems necessary to prevent a segfault on exit
        if selected is None:
            return
        enabled = selected.count() > 0
        self.ui.actionDuplicateObject.setEnabled(enabled)
        self.ui.actionDeleteObject.setEnabled(enabled)
        self.ui.actionCopyObject.setEnabled(enabled)

    def clipboardDataChanged(self):
        text = QApplication.clipboard().text()
        enabled = len(text) > 0 and text.startswith("IDF,")
        self.ui.actionPasteObject.setEnabled(enabled)

    def changedObjectCountToClass(self, parent, first, last):
        qindex = self.ui.listView.currentIndex()
        count = len(self.doc.objectsOfClass(self.selectedClass()))
        self.ui.listView.model().setData(qindex, "[{0:04d}] {1}".format(count, self.selectedClass()))

    # ------------------------------------------------------------------------
    # UI Actions
    # ------------------------------------------------------------------------

    def actionOpenFile(self):
        path = QFileDialog.getOpenFileName(self,
                                           "Open File", ".",
                                           "*.idf\n*.expidf")
        print(path)
        if path != '':
            self.openFile(path)

    def actionSaveFile(self):
        if self.currentfile == '':
            self.actionSaveFileAs()
        else:
            self.saveFile()

    def actionSaveFileAs(self):
        path = QFileDialog.getSaveFileName(self,
                                           "Save File", ".",
                                           "*.idf")
        if path != '':
            self.saveFileAs(path)

    def actionShowClassesWithObjectsOnly(self):
        self.showClassesWithObjectsOnly(self.ui.actionShowClassesWithObjectsOnly.isChecked())

    def actionNewObject(self):
        self.addNewObject()

    def actionDuplicateObject(self):
        self.duplicateObject()

    def actionDeleteObject(self):
        self.deleteObject()

    def actionClassClicked(self, index):
        self.selectClassAtIndex(index.row())

    # ------------------------------------------------------------------------

    def openFile(self, filepath):
        self.doc.readFromFile(filepath)
        self.currentfile = os.path.join(os.getcwd(), filepath)
        self.showClassesWithObjectsOnly(False)
        self.selectClassAtIndex(0)

    def saveFile(self):
        if os.path.exists(self.currentfile):
            self.doc.writeToFile(self.currentfile)

    def saveFileAs(self, filepath):
        self.doc.writeToFile(filepath)
        self.currentfile = os.path.join(os.getcwd(), filepath)

    def showClassesWithObjectsOnly(self, state):
        self.ui.actionShowClassesWithObjectsOnly.setChecked(state)
        if state and not self.doc.isEmpty():
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

    def selectedObject(self):
        qindex = self.ui.tableView.currentIndex()
        return self.doc.objectOfClassAtIndex(self.selectedClass(), qindex.column())

    def textInClassSelector(self, className):
        try:
            index = self.classes().index(className)
            qindex = self.ui.listView.model().createIndex(index, 0)
            return self.ui.listView.model().data(qindex, Qt.DisplayRole)
        except ValueError:
            return ""

    def addNewObject(self):
        self.ui.tableView.model().insertColumns(0, 1)

    def duplicateObject(self):
        # add column after last one
        model = self.ui.tableView.model()
        lastcol_index = model.columnCount()
        self.ui.tableView.model().insertColumns(lastcol_index, 1)

        # populate data
        obj = self.selectedObject()
        self.doc.replaceObjectAtIndexWithObject(lastcol_index, copy.deepcopy(obj))

    def deleteObject(self):
        self.ui.tableView.model().removeColumns(self.ui.tableView.currentIndex().column(), 1)

    def copyObject(self):
        obj = self.selectedObject()
        QApplication.clipboard().setText("IDF," + ",".join(obj) + ";")

    def pasteObject(self):
        # remove last character, supposed to be a colon
        clipObj = QApplication.clipboard().text()[:-1]
        obj = clipObj.split(",")
        # remove "IDF" prefix
        obj = obj[1:]

        self.addNewObject()
        lastcol_index = self.ui.tableView.model().columnCount() - 1
        self.doc.replaceObjectAtIndexWithObject(lastcol_index, obj)

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
        if (role == Qt.DisplayRole or role == Qt.EditRole) and self.classname:
            obj = self.doc.objectOfClassAtIndex(self.classname, index.column())
            # the first item is the object's class name
            return obj[index.row() + 1]

        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Vertical:
            return self.doc.fieldsOfClass(self.classname)[section]

        return None

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def setData(self, index, value, role=Qt.EditRole):
        obj = self.doc.objectOfClassAtIndex(self.classname, index.column())
        obj[index.row() + 1] = value
        self.doc.replaceObjectAtIndexWithObject(index.column(), obj)
        return True

    def insertColumns(self, column, count, parent=QModelIndex()):
        lastrow = self.rowCount(parent) + 1
        self.beginInsertColumns(parent, lastrow, lastrow)
        self.doc.addEmptyObject(self.classname)
        self.endInsertColumns()

    def removeColumns(self, column, count, parent=QModelIndex()):
        if column >= 0:
            self.beginRemoveColumns(parent, column, column)
            self.doc.deleteObjectOfClassAtIndex(self.classname, column)
            self.endRemoveColumns()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = IdfEditorWindow()
    frame.show()
    app.exec_()
