# -*- coding: utf-8 -*-
# @Time    : 2016/12/18 下午2:08
# @Author  : Zhixin Piao 
# @Email   : piaozhx@seu.edu.cn

from widget import ListWidget, CodeWidget, HtmlWidget


class WidgetManager:
    def __init__(self):
        self.WidgetDict = {}
        self.current = 'list'
        self.WidgetDict['list'] = ListWidget()
        self.WidgetDict['list'].readTables()
        self.WidgetDict['code'] = CodeWidget()
        self.WidgetDict['code'].hide()
        self.WidgetDict['html'] = HtmlWidget()
        self.WidgetDict['html'].hide()

    def getCurrentWidget(self):
        return self.WidgetDict[self.current]

    def changeCurrentWidget(self, name):
        self.WidgetDict[self.current].hide()
        self.WidgetDict[name].setVisible(True)
        self.current = name
