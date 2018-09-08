# -*- coding: utf-8 -*-
# @Time    : 2016/12/23 下午9:31
# @Author  : Zhixin Piao 
# @Email   : piaozhx@seu.edu.cn

from PyQt4.QtGui import *
from PyQt4.QtCore import *


# 文本编辑器的语法高亮
class MyHighlighter(QSyntaxHighlighter):
    def __init__(self, parent, theme):
        QSyntaxHighlighter.__init__(self, parent)
        self.parent = parent
        keyword = QTextCharFormat()
        reservedClasses = QTextCharFormat()
        assignmentOperator = QTextCharFormat()
        delimiter = QTextCharFormat()
        specialConstant = QTextCharFormat()
        boolean = QTextCharFormat()
        number = QTextCharFormat()
        comment = QTextCharFormat()
        string = QTextCharFormat()
        singleQuotedString = QTextCharFormat()

        self.highlightingRules = []

        # keyword
        brush = QBrush(Qt.darkBlue, Qt.SolidPattern)
        keyword.setForeground(brush)
        keyword.setFontWeight(QFont.Bold)
        keywords = QStringList(["break", "else", "for", "if", "in",
                                "next", "repeat", "return", "switch",
                                "try", "while"])
        for word in keywords:
            pattern = QRegExp("\\b" + word + "\\b")
            rule = HighlightingRule(pattern, keyword)
            self.highlightingRules.append(rule)

        # reservedClasses
        reservedClasses.setForeground(brush)
        reservedClasses.setFontWeight(QFont.Bold)
        keywords = QStringList(["array", "character", "complex",
                                "data.frame", "double", "factor",
                                "function", "integer", "list",
                                "logical", "matrix", "numeric",
                                "vector"])
        for word in keywords:
            pattern = QRegExp("\\b" + word + "\\b")
            rule = HighlightingRule(pattern, reservedClasses)
            self.highlightingRules.append(rule)

        # assignmentOperator
        brush = QBrush(Qt.blue, Qt.SolidPattern)
        pattern = QRegExp("(<){1,2}-")
        assignmentOperator.setForeground(brush)
        assignmentOperator.setFontWeight(QFont.Bold)
        rule = HighlightingRule(pattern, assignmentOperator)
        self.highlightingRules.append(rule)

        # delimiter
        pattern = QRegExp("[\)\(]+|[\{\}]+|[][]+")
        delimiter.setForeground(brush)
        delimiter.setFontWeight(QFont.Bold)
        rule = HighlightingRule(pattern, delimiter)
        self.highlightingRules.append(rule)

        # specialConstant
        brush = QBrush(Qt.blue, Qt.SolidPattern)
        specialConstant.setForeground(brush)
        keywords = QStringList(["Inf", "NA", "NaN", "NULL"])
        for word in keywords:
            pattern = QRegExp("\\b" + word + "\\b")
            rule = HighlightingRule(pattern, specialConstant)
            self.highlightingRules.append(rule)

        # boolean
        boolean.setForeground(brush)
        keywords = QStringList(["TRUE", "FALSE"])
        for word in keywords:
            pattern = QRegExp("\\b" + word + "\\b")
            rule = HighlightingRule(pattern, boolean)
            self.highlightingRules.append(rule)

        # number
        pattern = QRegExp("[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?")
        pattern.setMinimal(True)
        number.setForeground(brush)
        rule = HighlightingRule(pattern, number)
        self.highlightingRules.append(rule)

        # comment
        brush = QBrush(Qt.blue, Qt.SolidPattern)
        pattern = QRegExp("#[^\n]*")
        comment.setForeground(brush)
        rule = HighlightingRule(pattern, comment)
        self.highlightingRules.append(rule)

        # line number
        brush = QBrush(Qt.red, Qt.SolidPattern)
        pattern = QRegExp("[0-9]{4}:")
        comment.setForeground(brush)
        rule = HighlightingRule(pattern, comment)
        self.highlightingRules.append(rule)

        # string
        brush = QBrush(Qt.red, Qt.SolidPattern)
        pattern = QRegExp("\".*\"")
        pattern.setMinimal(True)
        string.setForeground(brush)
        rule = HighlightingRule(pattern, string)
        self.highlightingRules.append(rule)

        # singleQuotedString
        pattern = QRegExp("\'.*\'")
        pattern.setMinimal(True)
        singleQuotedString.setForeground(brush)
        rule = HighlightingRule(pattern, singleQuotedString)
        self.highlightingRules.append(rule)

    def highlightBlock(self, text):
        for rule in self.highlightingRules:
            expression = QRegExp(rule.pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, rule.format)
                index = text.indexOf(expression, index + length)
        self.setCurrentBlockState(0)


# 文本编辑器的语法高亮规则
class HighlightingRule():
    def __init__(self, pattern, format):
        self.pattern = pattern
        self.format = format


# 带行号的文本编辑框
class CodeEditor2(QFrame):
    class NumberBar(QWidget):

        def __init__(self, edit):
            QWidget.__init__(self, edit)

            self.edit = edit
            self.adjustWidth(1)

        def paintEvent(self, event):
            self.edit.numberbarPaint(self, event)
            QWidget.paintEvent(self, event)

        def adjustWidth(self, count):
            width = self.fontMetrics().width(unicode(count)) + 10
            if self.width() != width:
                self.setFixedWidth(width)

        def updateContents(self, rect, scroll):
            if scroll:
                self.scroll(0, scroll)
            else:
                # It would be nice to do
                # self.update(0, rect.y(), self.width(), rect.height())
                # But we can't because it will not remove the bold on the
                # current line if word wrap is enabled and a new block is
                # selected.
                self.update()

    class PlainTextEdit(QPlainTextEdit):

        def __init__(self, *args):
            QPlainTextEdit.__init__(self, *args)

            self.setFrameStyle(QFrame.NoFrame)
            self.highlight()
            # self.setLineWrapMode(QPlainTextEdit.NoWrap)

            self.cursorPositionChanged.connect(self.highlight)

        def highlight(self):
            hi_selection = QTextEdit.ExtraSelection()

            hi_selection.format.setBackground(self.palette().alternateBase())
            hi_selection.format.setProperty(QTextFormat.FullWidthSelection, QVariant(True))
            hi_selection.cursor = self.textCursor()
            hi_selection.cursor.clearSelection()

            self.setExtraSelections([hi_selection])

        def numberbarPaint(self, number_bar, event):
            font_metrics = self.fontMetrics()
            current_line = self.document().findBlock(self.textCursor().position()).blockNumber() + 1

            block = self.firstVisibleBlock()
            line_count = block.blockNumber()
            painter = QPainter(number_bar)
            painter.fillRect(event.rect(), self.palette().base())

            # Iterate over all visible text blocks in the document.
            while block.isValid():
                line_count += 1  # 行号
                block_top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()

                # Check if the position of the block is out side of the visible
                # area.
                if not block.isVisible() or block_top >= event.rect().bottom():
                    break

                # # We want the line number for the selected line to be bold.
                # if line_count == current_line:
                #     font = painter.font()
                #     font.setBold(True)
                #     painter.setFont(font)
                # else:
                #     font = painter.font()
                #     font.setBold(False)
                #     painter.setFont(font)

                # Draw the line number right justified at the position of the line.
                paint_rect = QRect(0, block_top, number_bar.width(), font_metrics.height())
                painter.drawText(paint_rect, Qt.AlignLeft, unicode(line_count))

                block = block.next()

                # painter.end()

    def __init__(self, *args):
        QFrame.__init__(self, *args)

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)

        self.edit = self.PlainTextEdit()
        self.number_bar = self.NumberBar(self.edit)

        hbox = QHBoxLayout(self)
        hbox.setSpacing(0)
        hbox.setMargin(0)
        hbox.addWidget(self.number_bar)
        hbox.addWidget(self.edit)

        self.edit.blockCountChanged.connect(self.number_bar.adjustWidth)

        self.edit.updateRequest.connect(self.number_bar.updateContents)

        # 设置字体
        font = QFont()
        font.setFamily("Monaco")
        font.setPointSize(14)
        self.setFont(font)

        # 语法高亮
        # MyHighlighter(self.edit, "Classic")

    def get_text(self):
        return str(self.edit.toPlainText())

    def sett_text(self, text):
        self.edit.setPlainText(text)


class CodeEditor(QTextEdit):
    def __init__(self, parent=None):
        QTextEdit.__init__(self, parent)
        # self.sett_text("1\n2\n3")
        # print self.document().blockCount()
        # a = QTextDocument()
        # a.blockCount()
        self.setAcceptRichText(False)
        MyHighlighter(self, "Classic")

    def get_text(self):
        return str(self.toPlainText())

    def sett_text(self, text):
        self.setPlainText(text)
