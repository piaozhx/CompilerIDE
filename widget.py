# -*- coding: utf-8 -*-
# @Time    : 2016/12/18 下午2:09
# @Author  : Zhixin Piao 
# @Email   : piaozhx@seu.edu.cn

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *
from item import MainList, MainTable


class CodeList(MainList):
    def __init__(self):
        MainList.__init__(self)
        self.clicked.connect(self.changeViewer)

    def connectViewer(self, viewer):
        self.viewer = viewer

    def changeViewer(self, item):
        filename = str(item.data().toString())
        self.viewer.setCode(filename)

    def feedTitle(self, title):
        item = QListWidgetItem(QIcon('../icon/list.png'), title)
        item.setSizeHint(QSize(140, 40))
        self.addItem(item)


class CodeWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        layout = QHBoxLayout()
        self.list = CodeList()
        self.codeView = CodeViewer()
        self.list.connectViewer(self.codeView)

        for filename in self.codeView.getCodelist():
            self.list.feedTitle(filename)

        layout.addWidget(self.list)
        layout.addWidget(self.codeView)

        self.setLayout(layout)
        self.setMinimumWidth(840)


class HtmlList(MainList):
    def __init__(self, parent=None):
        MainList.__init__(self)
        self.clicked.connect(self.changeViewer)
        # QModelIndex().data().toString()

    def connectViewer(self, viewer):
        self.viewer = viewer

    def changeViewer(self, item):
        filename = str(item.data().toString())
        self.viewer.setCode(filename)

    def feedTitle(self, title):
        item = QListWidgetItem(QIcon('../icon/list.png'), title)
        item.setSizeHint(QSize(140, 40))
        self.addItem(item)


class HtmlViewer(QWebView):
    def __init__(self, *args):
        QWebView.__init__(self)
        self.HtmlLex = LexerManager('html')

    def setCode(self, filename):
        self.setHtml(self.HtmlLex.getCode(filename))

    def getCodelist(self):
        return self.HtmlLex.codeDict.keys()


class HtmlWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        layout = QHBoxLayout()
        self.list = HtmlList()
        self.htmlView = HtmlViewer()
        self.list.connectViewer(self.htmlView)

        for filename in self.htmlView.getCodelist():
            self.list.feedTitle(filename)

        layout.addWidget(self.list)
        layout.addWidget(self.htmlView)

        self.setLayout(layout)
        self.setMinimumWidth(840)


class ListList(MainList):
    def __init__(self, parent=None):
        MainList.__init__(self)
        self.clicked.connect(self.changeTable)

    def connectTable(self, table):
        self.table = table

    def changeTable(self, item):
        self.table.displayTable(item.row())

    def feedTitle(self, title):
        item = QListWidgetItem(QIcon('../icon/list.png'), title)
        item.setSizeHint(QSize(140, 40))
        self.addItem(item)


class ListWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        layout = QHBoxLayout()

        self.table = MainTable()
        self.list = ListList()
        self.list.connectTable(self.table)

        layout.addWidget(self.list)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.setMinimumWidth(840)

    def readTables(self):
        tables = tableManager().getTable()
        self.table.setTables(tables)

        for i in range(len(tables)):
            self.list.feedTitle(u'第%d个表格' % (i + 1))

        self.table.displayTable(0)
        self.list.setCurrentRow(0)
