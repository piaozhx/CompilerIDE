# -*- coding: utf-8 -*-
# @Time    : 2016/12/18 下午2:59
# @Author  : Zhixin Piao 
# @Email   : piaozhx@seu.edu.cn

from lex import *
from yacc import *
import ply.lex as lex
import ply.yacc as yacc


class Compiler:
    def __init__(self):
        self.lexer = lex.lex()
        self.yaccer = yacc.yacc()
        self.tokens = []
        self.code = ''

    # parse asm code from path
    def parse(self, c_code):
        s = str(c_code).lower()

        # lexical analysis
        self.lexer.input(s)
        self.tokens = []
        for token in self.lexer:
            self.tokens.append(token)

        # syntactic analysis
        self.yaccer.parse(s)
        self.code = res_code[0]

        return self.code

    # print token by lexer
    def print_token(self):
        for token in self.tokens:
            print token

    # get code produce by yacc
    def get_code(self):
        return self.code
