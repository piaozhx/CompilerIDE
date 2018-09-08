# -*- coding: utf-8 -*-
# @Time    : 2016/12/18 下午1:54
# @Author  : Zhixin Piao 
# @Email   : piaozhx@seu.edu.cn

from PyQt4.QtGui import *
from PyQt4.QtCore import *


class MainList(QListWidget):
    def __init__(self, parent=None):
        QListWidget.__init__(self, parent)

        self.setMaximumWidth(170)
        self.setMinimumWidth(170)

        p = self.palette()
        p.setColor(QPalette.Text, QColor(255, 255, 255))
        p.setColor(QPalette.Base, QColor(39, 39, 39))
        self.setPalette(p)

        self.setFont(QFont(u"微软雅黑", 13))

        self.setFrameShape(QListWidget.NoFrame)
        self.verticalScrollBar().setStyleSheet(open('../qss/ScrollBarStyle.qss', 'r').read())


class MainTable(QTableWidget):
    def __init__(self, parent=None):
        QTableWidget.__init__(self, parent)

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        self.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setDefaultSectionSize(40)
        self.setShowGrid(False)
        self.setAutoFillBackground(True)
        self.setFont(QFont(u"微软雅黑", 12))

        p = self.palette()
        p.setColor(QPalette.Text, QColor(255, 255, 255))
        p.setColor(QPalette.Base, QColor(34, 34, 34))
        p.setColor(QPalette.Background, QColor(34, 34, 34))
        p.setColor(QPalette.AlternateBase, QColor(39, 39, 39))
        self.setPalette(p)
        self.setFocusPolicy(Qt.NoFocus)
        self.setAlternatingRowColors(True);
        self.setFrameShape(QListWidget.NoFrame)
        self.setStyleSheet('QTableView {selection-background-color: #FFFFFF; selection-color: #000000;}')
        self.verticalScrollBar().setStyleSheet(open('../qss/ScrollBarStyle.qss', 'r').read())

    # 设置table
    def displayTable(self, i):
        table = self.tables[i]
        col_count = len(table)
        row_count = len(table[0])
        self.setColumnCount(col_count)
        self.setRowCount(row_count)

        for i in range(col_count):
            for j in range(row_count):
                self.setItem(j, i, QTableWidgetItem(table[i][j]))

        self.setCurrentCell(0, 0)

    def changeItem(self, index):
        item = self.item(index.column(), index.row())
        item.setBackground(Qt.white)

    # 初始化表格数据
    def setTables(self, tables):
        self.tables = tables


class WhiteLabel(QLabel):
    def __init__(self, parent=None):
        QLabel.__init__(self, parent)

        self.setFont(QFont(u"微软雅黑", 12))
        self.setStyleSheet('color:#FFFFFF')


class TitleBar(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.setStyleSheet(open("../qss/TitleBarStyle.qss", 'r').read())

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(QPalette.Background, QColor(39, 39, 39))
        self.setPalette(p)

        # 控件设置
        icon = QLabel()
        icon.setPixmap(QPixmap("../icon/linker.png").scaled(1024 / 20, 598 / 20))

        title = WhiteLabel("Entity Linker 1.0 Test")

        btn_close = QToolButton(self)
        btn_close.setIcon(QIcon("../icon/close.png"))
        btn_close.setIconSize(QSize(20, 30))
        btn_close.clicked.connect(self.close)

        btn_min = QToolButton(self)
        btn_min.setIcon(QIcon("../icon/min.png"))
        btn_min.setIconSize(QSize(20, 30))
        btn_min.clicked.connect(self.min)

        btn_max = QToolButton(self)
        btn_max.setIcon(QIcon("../icon/max.png"))
        btn_max.setIconSize(QSize(20, 30))
        btn_max.clicked.connect(self.max)
        self.max_flag = False

        btn_menu = QToolButton(self)
        btn_menu.setIcon(QIcon("../icon/menu.png"))
        btn_menu.setIconSize(QSize(20, 30))

        # 布局设置
        layout = QHBoxLayout()
        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(btn_menu)
        layout.addWidget(btn_min)
        layout.addWidget(btn_max)
        layout.addWidget(btn_close)
        layout.insertStretch(2)
        self.setLayout(layout)

        self.setMaximumHeight(40)
        self.setMinimumHeight(40)

    def min(self):
        self.box.showMinimized()

    def max(self):
        if self.max_flag:
            self.box.showNormal()
        else:
            self.box.showMaximized()
        self.max_flag = not self.max_flag

    def close(self):
        self.box.exit()

    def setMainWindow(self, mainwindow):
        self.box = mainwindow

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.box.moving = True
            self.box.offset = event.pos()

    def mouseMoveEvent(self, event):
        self.box.move(event.globalPos() - self.box.offset)


class ToolBtn(QToolButton):
    def __init__(self, icon, name):
        QPushButton.__init__(self)
        self.setIcon(icon)
        self.setText(name)
        self.setFont(QFont(u"微软雅黑", 10))
        self.setIconSize(QSize(40, 50))
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        p = self.palette()
        p.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        self.setPalette(p)


class ToolBar(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setStyleSheet(open("../qss/ToolBarStyle.qss", 'r').read())
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(QPalette.Background, QColor(49, 49, 49))
        self.setPalette(p)

        btn_list = ToolBtn(QIcon("../icon/tool_list.png"), "list")
        btn_list.setChecked(True)
        btn_list.clicked.connect(lambda: self.changeFrame('list'))

        btn_html = ToolBtn(QIcon("../icon/html.png"), "html")
        btn_html.clicked.connect(lambda: self.changeFrame('html'))

        btn_text = ToolBtn(QIcon("../icon/text.png"), "text")
        btn_import = ToolBtn(QIcon("../icon/import.png"), "import")

        btn_code = ToolBtn(QIcon("../icon/code.png"), "code")
        btn_code.clicked.connect(lambda: self.changeFrame('code'))

        btn_work = ToolBtn(QIcon("../icon/work3.png"), "run")

        layout = QHBoxLayout()

        layout.addWidget(btn_list)
        layout.addWidget(btn_html)
        layout.addWidget(btn_text)
        layout.addWidget(btn_import)
        layout.addWidget(btn_code)
        layout.addWidget(btn_work)
        layout.setMargin(0)
        layout.setSpacing(0)

        self.setLayout(layout)
        self.setMaximumHeight(65)
        self.setMinimumHeight(65)

    def changeFrame(self, name):
        self.widgetMgr.changeCurrentWidget(name)

    def setWidgetManager(self, widgetManager):
        self.widgetMgr = widgetManager