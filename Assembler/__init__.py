# -*- coding: utf-8 -*-
# @Time    : 2016/12/18 下午12:47
# @Author  : Zhixin Piao 
# @Email   : piaozhx@seu.edu.cn

from lex import *
from yacc import *
import ply.lex as lex
import ply.yacc as yacc


class Assembler:
    def __init__(self):
        self.lexer = lex.lex()

        # init_assembler_variables()
        self.yaccer = yacc.yacc()
        self.tokens = []
        self.code = ''

    # parse asm code from path
    def parse(self, asm_code):
        s = str(asm_code).lower()

        # lexical analysis
        self.lexer.input(s)
        self.tokens = []
        for token in self.lexer:
            self.tokens.append(token)

        # syntactic analysis
        self.yaccer.parse(s)

        self.code = ''
        for i, data_code in enumerate(res_code['data']):
            self.code += '%s\n' % data_code if i < 2 else '%s,\n' % data_code

        self.code += '\n%s\n\n' % ('=' * 32)

        for i, text_code in enumerate(res_code['text']):
            self.code += '%s\n' % text_code if i < 2 else '%s,\n' % text_code

        return self.code

    # print token by lexer
    def print_token(self):
        for token in self.tokens:
            print token

    # get code produce by yacc
    def get_code(self):
        return self.code
