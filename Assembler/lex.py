# -*- coding: utf-8 -*-
# @Time    : 2016/12/18 下午12:47
# @Author  : Zhixin Piao 
# @Email   : piaozhx@seu.edu.cn

# Tokens
tokens = ['NUMBER', 'REG', 'VARIABLE']
literals = ['=', '+', '-', '*', '/', '(', ')', ':', '.']
reserved = {
    # R-instruction
    'add': 'ADD',
    'addu': 'ADDU',
    'sub': 'SUB',
    'subu': 'SUBU',
    'and': 'AND',
    'mult': 'MULT',
    'multu': 'MULTU',
    'div': 'DIV',
    'divu': 'DIVU',
    'mfhi': 'MFHI',
    'mflo': 'MFLO',
    'mthi': 'MTHI',
    'mtlo': 'MTLO',
    'mfc0': 'MFC0',
    'mtc0': 'MTC0',
    'or': 'OR',
    'xor': 'XOR',
    'nor': 'NOR',
    'slt': 'SLT',
    'sltu': 'SLTU',
    'sll': 'SLL',
    'srl': 'SRL',
    'sra': 'SRA',
    'sllv': 'SLLV',
    'srlv': 'SRLV',
    'srav': 'SRAV',
    'jr': 'JR',
    'jalr': 'JALR',
    'break': 'BREAK',
    'syscall': 'SYSCALL',
    'eret': 'ERET',

    # I-instruction
    'addi': 'ADDI',
    'addiu': 'ADDIU',
    'andi': 'ANDI',
    'ori': 'ORI',
    'xori': 'XORI',
    'lui': 'LUI',
    'lb': 'LB',
    'lbu': 'LBU',
    'lh': 'LH',
    'lhu': 'LHU',
    'sb': 'SB',
    'sh': 'SH',
    'lw': 'LW',
    'sw': 'SW',
    'beq': 'BEQ',
    'bne': 'BNE',
    'bgez': 'BGEZ',
    'bgtz': 'BGTZ',
    'blez': 'BLEZ',
    'bltz': 'BLTZ',
    'bgezal': 'BGEZAL',
    'bltzal': 'BLTZAL',
    'slti': 'SLTI',
    'sltiu': 'SLTIU',

    # J-instruction
    'j': 'J',
    'jal': 'JAL',

    # word-type
    'dw': 'WORDTYPE',
    'word': 'WORDTYPE',

    # other
    'data': 'DATA',
    'text': 'TEXT',
}

reg_name = {
    '$zero': '$0',
    '$at': '$1',
    '$v0': '$2',
    '$v1': '$3',
    '$a0': '$4',
    '$a1': '$5',
    '$a2': '$6',
    '$a3': '$7',
    '$t0': '$8',
    '$t1': '$9',
    '$t2': '$10',
    '$t3': '$11',
    '$t4': '$12',
    '$t5': '$13',
    '$t6': '$14',
    '$t7': '$15',
    '$s0': '$16',
    '$s1': '$17',
    '$s2': '$18',
    '$s3': '$19',
    '$s4': '$20',
    '$s5': '$21',
    '$s6': '$22',
    '$s7': '$23',
    '$t8': '$24',
    '$t9': '$25',
    '$k0': '$26',
    '$k1': '$27',
    '$gp': '$28',
    '$sp': '$29',
    '$s8': '$30',
    '$fp': '$30',
    '$ra': '$31'
}

tokens += set(reserved.values())

# Re
t_ignore = " \t,"


def t_VARIABLE(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'VARIABLE')
    return t


def t_REG(t):
    r'\$[a-z0-9A-Z]+'
    t.value = reg_name.get(t.value.lower(), t.value)
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
    r'\#.*'
