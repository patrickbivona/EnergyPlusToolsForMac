# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'idf_editor.ui'
#
# Created: Tue Dec 31 15:16:45 2013
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(800, 600)
        MainWindow.setUnifiedTitleAndToolBarOnMac(False)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.listView = QtGui.QListView(self.splitter)
        self.listView.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.listView.sizePolicy().hasHeightForWidth())
        self.listView.setSizePolicy(sizePolicy)
        self.listView.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.listView.setObjectName(_fromUtf8("listView"))
        self.tableView = QtGui.QTableView(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.tableView.sizePolicy().hasHeightForWidth())
        self.tableView.setSizePolicy(sizePolicy)
        self.tableView.setObjectName(_fromUtf8("tableView"))
        self.verticalLayout.addWidget(self.splitter)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuView = QtGui.QMenu(self.menubar)
        self.menuView.setObjectName(_fromUtf8("menuView"))
        self.menuEdit = QtGui.QMenu(self.menubar)
        self.menuEdit.setObjectName(_fromUtf8("menuEdit"))
        self.menuObject = QtGui.QMenu(self.menuEdit)
        self.menuObject.setObjectName(_fromUtf8("menuObject"))
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtGui.QToolBar(MainWindow)
        self.toolBar.setMovable(False)
        self.toolBar.setIconSize(QtCore.QSize(16, 16))
        self.toolBar.setFloatable(True)
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionOpen = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/16x16/document-open.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionOpen.setIcon(icon)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.actionSaveAs = QtGui.QAction(MainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/16x16/document-save-as.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSaveAs.setIcon(icon1)
        self.actionSaveAs.setObjectName(_fromUtf8("actionSaveAs"))
        self.actionClose = QtGui.QAction(MainWindow)
        self.actionClose.setObjectName(_fromUtf8("actionClose"))
        self.actionSave = QtGui.QAction(MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/16x16/document-save.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSave.setIcon(icon2)
        self.actionSave.setObjectName(_fromUtf8("actionSave"))
        self.actionShowClassesWithObjectsOnly = QtGui.QAction(MainWindow)
        self.actionShowClassesWithObjectsOnly.setCheckable(True)
        self.actionShowClassesWithObjectsOnly.setObjectName(_fromUtf8("actionShowClassesWithObjectsOnly"))
        self.actionNewObject = QtGui.QAction(MainWindow)
        self.actionNewObject.setObjectName(_fromUtf8("actionNewObject"))
        self.actionDeleteObject = QtGui.QAction(MainWindow)
        self.actionDeleteObject.setEnabled(False)
        self.actionDeleteObject.setObjectName(_fromUtf8("actionDeleteObject"))
        self.actionCopyObject = QtGui.QAction(MainWindow)
        self.actionCopyObject.setEnabled(False)
        self.actionCopyObject.setObjectName(_fromUtf8("actionCopyObject"))
        self.actionDuplicateObject = QtGui.QAction(MainWindow)
        self.actionDuplicateObject.setEnabled(False)
        self.actionDuplicateObject.setObjectName(_fromUtf8("actionDuplicateObject"))
        self.actionPasteObject = QtGui.QAction(MainWindow)
        self.actionPasteObject.setEnabled(False)
        self.actionPasteObject.setObjectName(_fromUtf8("actionPasteObject"))
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSaveAs)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionClose)
        self.menuView.addAction(self.actionShowClassesWithObjectsOnly)
        self.menuObject.addAction(self.actionNewObject)
        self.menuObject.addAction(self.actionDuplicateObject)
        self.menuObject.addAction(self.actionDeleteObject)
        self.menuObject.addAction(self.actionCopyObject)
        self.menuObject.addAction(self.actionPasteObject)
        self.menuEdit.addAction(self.menuObject.menuAction())
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.toolBar.addAction(self.actionOpen)
        self.toolBar.addAction(self.actionSave)
        self.toolBar.addAction(self.actionNewObject)
        self.toolBar.addAction(self.actionDuplicateObject)
        self.toolBar.addAction(self.actionDeleteObject)
        self.toolBar.addAction(self.actionCopyObject)
        self.toolBar.addAction(self.actionPasteObject)

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.actionClose, QtCore.SIGNAL(_fromUtf8("triggered()")), MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.menuView.setTitle(_translate("MainWindow", "View", None))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit", None))
        self.menuObject.setTitle(_translate("MainWindow", "Object", None))
        self.menuHelp.setTitle(_translate("MainWindow", "Help", None))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar", None))
        self.actionOpen.setText(_translate("MainWindow", "Open...", None))
        self.actionOpen.setShortcut(_translate("MainWindow", "Ctrl+O", None))
        self.actionSaveAs.setText(_translate("MainWindow", "Save As...", None))
        self.actionSaveAs.setShortcut(_translate("MainWindow", "Ctrl+Shift+S", None))
        self.actionClose.setText(_translate("MainWindow", "Close", None))
        self.actionClose.setShortcut(_translate("MainWindow", "Ctrl+W", None))
        self.actionSave.setText(_translate("MainWindow", "Save", None))
        self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S", None))
        self.actionShowClassesWithObjectsOnly.setText(_translate("MainWindow", "Show Classes with Objects Only", None))
        self.actionShowClassesWithObjectsOnly.setShortcut(_translate("MainWindow", "Ctrl+L", None))
        self.actionNewObject.setText(_translate("MainWindow", "New", None))
        self.actionNewObject.setIconText(_translate("MainWindow", "New Obj", None))
        self.actionNewObject.setToolTip(_translate("MainWindow", "New Object", None))
        self.actionNewObject.setShortcut(_translate("MainWindow", "Ctrl+N", None))
        self.actionDeleteObject.setText(_translate("MainWindow", "Delete", None))
        self.actionDeleteObject.setIconText(_translate("MainWindow", "Del Obj", None))
        self.actionDeleteObject.setToolTip(_translate("MainWindow", "Delete Object", None))
        self.actionCopyObject.setText(_translate("MainWindow", "Copy", None))
        self.actionCopyObject.setIconText(_translate("MainWindow", "Copy Obj", None))
        self.actionCopyObject.setToolTip(_translate("MainWindow", "Copy Object", None))
        self.actionDuplicateObject.setText(_translate("MainWindow", "Duplicate", None))
        self.actionDuplicateObject.setIconText(_translate("MainWindow", "Dup Obj", None))
        self.actionDuplicateObject.setToolTip(_translate("MainWindow", "Duplicate Object", None))
        self.actionPasteObject.setText(_translate("MainWindow", "Paste", None))
        self.actionPasteObject.setIconText(_translate("MainWindow", "Paste Obj", None))
        self.actionPasteObject.setToolTip(_translate("MainWindow", "Paste Object", None))

import idf_editor_rc
