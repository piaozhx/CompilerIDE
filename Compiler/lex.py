# -*- coding: utf-8 -*-
# @Time    : 2016/12/18 下午2:59
# @Author  : Zhixin Piao 
# @Email   : piaozhx@seu.edu.cn

# Tokens
tokens = ['NUMBER', 'VARIABLE']
literals = ['=', '+', '-', '*', '/', '(', ')', ':', '.', ';', '$', '[', ']', '|', '~', '&', '{', '}', '%', ',',
            '^', '!']
reserved = {
    "void": "VOID",
    "continue": "CONTINUE",
    "if": "IF",
    "while": "WHILE",
    "else": "ELSE",
    "break": "BREAK",
    "int": "INT",
    "return": "RETURN",
    "eret": "ERET"
}

# simple symbol which has no action
simple_symbol = {
    "\<=": "LE",
    "\>=": "GE",
    "\=\=": "EQ",
    "\!\=": "NE",
    "\<\<": "LSHIFT",
    "\>\>": "RSHIFT",
    "\|\|": "OR",
    "\&\&": "AND",
    "\<": "LT",
    "\>": "GT"

}

tokens += set(reserved.values())
tokens += set(simple_symbol.values())

# Re
t_ignore = " \t"
for symbol, name in simple_symbol.iteritems():
    exec ("t_%s = r'%s'" % (name, symbol))


def t_VARIABLE(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'VARIABLE')
    return t


def t_NUMBER(t):
    r'(0[Xx][0-9A-Fa-f]+)|(\d+)'
    if 'x' in t.value or 'X' in t.value:
        t.value = int(t.value[2:], 16)
    else:
        t.value = int(t.value)
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


def t_COMMENT(t):
    r'\/\/.*'
