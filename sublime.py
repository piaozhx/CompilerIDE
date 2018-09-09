# -*- coding: utf-8 -*-
# @Time    : 2016/12/19 上午10:05
# @Author  : Zhixin Piao 
# @Email   : piaozhx@seu.edu.cn

import sys
import traceback
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from Assembler import Assembler
from Compiler import Compiler
from CodeEditor import CodeEditor


class RunBtn(QPushButton):
    def __init__(self, parent=None):
        QPushButton.__init__(self, parent)

        self.setMaximumWidth(200)
        self.setMinimumWidth(100)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)


class LabelBtn(QPushButton):
    def __init__(self, parent=None):
        QPushButton.__init__(self, parent)

        self.setCheckable(True)
        self.setAutoExclusive(True)
        # self.setMinimumHeight(40)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


class DocBar(QFrame):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.label_btn_c = LabelBtn("C code")
        self.label_btn_asm = LabelBtn("ASM code")
        self.label_btn_coe = LabelBtn("COE code")
        self.label_btn_debug = LabelBtn("COE code (debug)")
        self.label_btn_c.setChecked(True)
        self.run_btn = RunBtn("Run")

        self.init_layout()
        self.decorate()

    def init_layout(self):
        layout = QHBoxLayout()

        layout.addWidget(self.run_btn)
        layout.addWidget(self.label_btn_c)
        layout.addWidget(self.label_btn_asm)
        layout.addWidget(self.label_btn_coe)
        layout.addWidget(self.label_btn_debug)
        layout.setContentsMargins(0, 0, 0, 0)
        # layout.setSpacing(0)
        # layout.insertStretch(100)

        self.setLayout(layout)
        self.decorate()

    def decorate(self):
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(QPalette.Base, QColor(34, 34, 34))
        p.setColor(QPalette.Background, QColor(34, 34, 34))
        self.setPalette(p)
        self.setMaximumHeight(40)
        self.setMinimumHeight(40)


class DocEditor(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.doc_bar = DocBar()
        self.editor = CodeEditor()
        self.console = None

        # c, asm, coe
        self.select = 'c'
        self.code = {'c': '', 'asm': '', 'coe': '', 'debug': ''}

        self.init_layout()
        self.init_action()

    def init_layout(self):
        layout = QVBoxLayout()

        layout.addWidget(self.doc_bar)
        layout.addWidget(self.editor)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.setStyleSheet(open("qss/ToolBarStyle.qss", 'r').read())

    def init_action(self):
        self.doc_bar.label_btn_c.clicked.connect(lambda: self.click_label('c'))
        self.doc_bar.label_btn_asm.clicked.connect(lambda: self.click_label('asm'))
        self.doc_bar.label_btn_coe.clicked.connect(lambda: self.click_label('coe'))
        self.doc_bar.label_btn_debug.clicked.connect(lambda: self.click_label('debug'))
        self.doc_bar.run_btn.clicked.connect(lambda: self.click_run())

        action = QAction('run', self)
        action.setShortcut('Ctrl+R')
        action.triggered.connect(lambda: self.click_run())
        self.addAction(action)

    def connect_console(self, console):
        self.console = console

    def click_label(self, label_name):
        self.code[self.select] = self.editor.get_text()
        self.editor.sett_text(self.code[label_name])
        self.select = label_name

    def click_run(self):
        self.console.setText("")

        if self.select == 'c':
            try:
                self.code['c'] = self.editor.get_text()
                self.code['asm'] = Compiler().parse(self.code['c'])
                self.code['coe'] = Assembler().parse(self.code['asm'])
                self.code['debug'] = self.get_debug_code()

                if str(self.console.toPlainText()) == "":
                    print 'successful complie c code!'
                else:
                    print 'failed complie c code!!!'
            except:
                print traceback.format_exc()
                print 'failed complie c code!!!'

        elif self.select == 'asm':
            try:
                self.code['asm'] = self.editor.get_text()
                self.code['coe'] = Assembler().parse(self.code['asm'])
                self.code['debug'] = self.get_debug_code()

                if str(self.console.toPlainText()) == "":
                    print 'successful complie asm code!'
                else:
                    print 'failed complie asm code!!!'
            except:
                print traceback.format_exc()
                print 'failed complie asm code!!!'

    def get_debug_code(self):
        asm_codes = self.code['asm'].split('\n')
        coe_data_codes, coe_text_codes = self.code['coe'].split('=' * 32)
        coe_data_codes = coe_data_codes.split('\n')
        coe_text_codes = coe_text_codes.split('\n')[2:]

        # update asm_code
        _temp = []
        for asm_code in asm_codes:
            if asm_code != '':
                _temp.append(asm_code)
        asm_codes = _temp

        res = ''


        # uodate coe data code
        len_coe_data = len(coe_data_codes) - 2
        len_coe_text = len(coe_text_codes) - 2
        line_asm = 0

        count = 0
        while count < len_coe_data:
            if coe_data_codes[count].find('=') != -1:
                res += ' ' * 6 + coe_data_codes[count] + '\n'
                count += 1
            else:
                if asm_codes[line_asm].find('.') == 0:
                    res += ' ' * 6 + '// %s\n' % asm_codes[line_asm]
                    line_asm += 1
                else:
                    res += '%.4d: %s // %s\n' % ((count-2) * 4, coe_data_codes[count], asm_codes[line_asm])
                    line_asm += 1
                    count += 1


        count = 0
        while count < len_coe_text:
            if coe_text_codes[count].find('=') != -1:
                res += ' ' * 6 + coe_text_codes[count] + '\n'
                count += 1
            else:
                if asm_codes[line_asm].find(':') != -1 or asm_codes[line_asm].find('.') == 0:
                    res += ' ' * 6 + '// %s\n' % asm_codes[line_asm]
                    line_asm += 1
                else:
                    res += '%.4d: %s // %s\n' % ((count-2) * 4, coe_text_codes[count], asm_codes[line_asm])
                    line_asm += 1
                    count += 1


        return res


class Console(QTextEdit):
    def __init__(self, parent=None):
        QTextEdit.__init__(self, parent)

        self.setReadOnly(True)
        self.setMinimumHeight(30)
        # self.setMaximumHeight(30)


class EmittingStream(QObject):
    textWritten = pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))


class TestApp(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.doc_editor = DocEditor()
        self.console = Console()
        self.doc_editor.connect_console(self.console)

        self.init_layout()
        self.init_action()
        self.center(1000, 1000)
        self.setWindowTitle("CompilerIDE")

    def init_layout(self):
        layout = QVBoxLayout()

        splitter1 = QSplitter(Qt.Vertical)
        splitter1.addWidget(self.doc_editor)
        splitter1.addWidget(self.console)
        splitter1.setHandleWidth(1)

        layout.addWidget(splitter1)
        layout.setSpacing(0)
        layout.setMargin(0)

        # set layout to mainwindow
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def init_action(self):
        # 重定向输出
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        sys.stderr = EmittingStream(textWritten=self.normalOutputWritten)

    # 主窗口居中显示并调整大小函数
    def center(self, width, height):
        self.resize(width, height)
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2 - 50)

    def normalOutputWritten(self, text):
        cursor = self.console.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.console.setTextCursor(cursor)
        self.console.ensureCursorVisible()

    def __del__(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = TestApp()
    mainWin.show()
    sys.exit(app.exec_())
