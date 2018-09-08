# -*- coding: utf-8 -*-
# @Time    : 2016/12/18 下午12:47
# @Author  : Zhixin Piao
# @Email   : piaozhx@seu.edu.cn

# Parsing rules
# 如果code不是从0开始的那么会有很严重的问题
# i-指令中offset 不需要 /4，使用的是真实地址
# 汇编中data_offset 与 text_offset是真实地址


res_code = {'data': [], 'text': []}

# some variables for assembler
names = {}
data_offset = 0
text_offset = 0
cur_data_addr = 0  # has been divided by 4
cur_text_addr = 0  # has been divided by 4

data_memory_set = {}  # key: addr; value: data, and this addr is real addr
label_set = {}  # key: label_name; value: addr, and this addr is real addr

# code data


# dictionary of op
op = {
    # R-instruction
    'add': '000000',
    'addu': '000000',
    'sub': '000000',
    'subu': '000000',
    'and': '000000',
    'mult': '000000',
    'multu': '000000',
    'div': '000000',
    'divu': '000000',
    'mfhi': '000000',
    'mflo': '000000',
    'mthi': '000000',
    'mtlo': '000000',
    'mfc0': '010000',
    'mtc0': '010000',
    'or': '000000',
    'xor': '000000',
    'nor': '000000',
    'slt': '000000',
    'sltu': '000000',
    'sll': '000000',
    'srl': '000000',
    'sra': '000000',
    'sllv': '000000',
    'srlv': '000000',
    'srav': '000000',
    'jr': '000000',
    'jalr': '000000',
    'break': '000000',
    'syscall': '000000',
    'eret': '010000',

    # I-instruction
    'addi': '001000',
    'addiu': '001001',
    'andi': '001100',
    'ori': '001101',
    'xori': '001110',
    'lui': '001111',
    'lb': '100000',
    'lbu': '100100',
    'lh': '100001',
    'lhu': '100101',
    'sb': '101000',
    'sh': '101001',
    'lw': '100011',
    'sw': '101011',
    'beq': '000100',
    'bne': '000101',
    'bgez': '000001',
    'bgtz': '000111',
    'blez': '000110',
    'bltz': '000001',
    'bgezal': '000001',
    'bltzal': '000001',
    'slti': '001010',
    'sltiu': '001011',

    # J-instruction
    'j': '000010',
    'jal': '000011'
}

# dictionary of func
func = {
    'add': '100000',
    'addu': '100001',
    'sub': '100010',
    'subu': '100011',
    'and': '100100',
    'mult': '011000',
    'multu': '011001',
    'div': '011010',
    'divu': '011011',
    'mfhi': '010000',
    'mflo': '010010',
    'mthi': '010001',
    'mtlo': '010011',
    'or': '100101',
    'xor': '100110',
    'nor': '100111',
    'slt': '101010',
    'sltu': '101011',
    'sll': '000000',
    'srl': '000010',
    'sra': '000011',
    'sllv': '000100',
    'srlv': '000110',
    'srav': '000111',
    'jr': '001000',
    'jalr': '001001',
    'break': '001101',
    'syscall': '001100',
    'eret': '011000',
}

# dictionary of reg number
reg_num = {
    '$0': '00000',
    '$1': '00001',
    '$2': '00010',
    '$3': '00011',
    '$4': '00100',
    '$5': '00101',
    '$6': '00110',
    '$7': '00111',
    '$8': '01000',
    '$9': '01001',
    '$10': '01010',
    '$11': '01011',
    '$12': '01100',
    '$13': '01101',
    '$14': '01110',
    '$15': '01111',
    '$16': '10000',
    '$17': '10001',
    '$18': '10010',
    '$19': '10011',
    '$20': '10100',
    '$21': '10101',
    '$22': '10110',
    '$23': '10111',
    '$24': '11000',
    '$25': '11001',
    '$26': '11010',
    '$27': '11011',
    '$28': '11100',
    '$29': '11101',
    '$30': '11110',
    '$31': '11111'
}


def extend_16(num):
    if type(num) == int:
        return '{0:016b}'.format(num if num >= 0 else num + (1 << 16))
    else:
        return num


def extend_26(num):
    if type(num) == int:
        return '{0:026b}'.format(num if num >= 0 else num + (1 << 26))
    else:
        return num


def extend_32(num):
    return '{0:032b}'.format(num)


def binary_to_hex(b):
    return '{0:08x}'.format(int(b, 2))


def main(codes):
    global res_code, names, data_offset, cur_data_addr, cur_text_addr, data_memory_set, label_set

    res_code['data'] = []
    res_code['text'] = []

    # set data part
    res_code['data'] = ['memory_initialization_radix = 2;', 'memory_initialization_vector =']

    if data_memory_set != {}:
        for i in xrange(data_offset / 4):
            res_code['data'].append('0' * 32)
        for data in data_memory_set.itervalues():
            if type(data) == int:
                res_code['data'].append(extend_32(data))
            else:
                for label, addr in label_set.iteritems():
                    if '##%s##' % label == data:
                        res_code['data'].append(extend_32(addr))

    # set code part
    res_code['text'] = ['memory_initialization_radix = 2;', 'memory_initialization_vector =']
    for i, ins in enumerate(codes):
        # &&label&& extend to 26 and divided by 4
        # ##label## extend to 16 and do nothing
        # !!label!! extend to 16 and compute the offset with current address
        if i == 1 and ins == "00000000000000000000000000100101":
            codes[i] = "01000000000110100000000000000001"
        elif i == 2 and ins == "00000000000000000000000000100101":
            codes[i] = "00000011010000000000000000001000"
        else:
            for label, addr in label_set.iteritems():
                if '&&%s&&' % label in ins:
                    codes[i] = codes[i].replace('&&%s&&' % label, extend_26(addr / 4))
                elif '##%s##' % label in ins:
                    codes[i] = codes[i].replace('##%s##' % label, extend_16(addr))
                elif '!!%s!!' % label in ins:
                    codes[i] = codes[i].replace('!!%s!!' % label, extend_16((addr - i * 4 - 4) / 4))

    res_code['text'] += codes

    names = {}
    data_offset = 0
    cur_data_addr = 0  # has been divided by 4
    cur_text_addr = 0  # has been divided by 4

    data_memory_set = {}  # key: addr; value: data, and this addr is real addr
    label_set = {}  # key: label_name; value: addr, and this addr is real addr


def p_start(p):
    '''start : data_statement texts
             | texts'''

    p[0] = p[2] if len(p) == 3 else p[1]
    main(p[0])


def p_data_statement(p):
    '''data_statement : '.' DATA define_datas
                      | '.' DATA NUMBER define_datas'''
    global data_offset
    if len(p) == 4:
        data_offset = 0
    else:
        data_offset = p[3]


def p_define_datas(p):
    '''define_datas : define_data
                    | define_datas define_data'''


def p_define_data(p):
    "define_data : VARIABLE ':' '.' WORDTYPE data"
    global cur_data_addr
    if p[4] == 'word':
        # 此处被修改, 原为 * 4
        label_set[p[1]] = cur_data_addr
        data_memory_set[cur_data_addr] = p[5]
        cur_data_addr += 1


def p_data(p):
    '''data : VARIABLE
            | NUMBER'''

    if type(p[1]) == int:
        p[0] = p[1]
    else:
        p[0] = "##%s##" % p[1]


# def p_datas(p):
#     '''datas : expression
#              | datas expression'''
#     if len(p) == 2:
#         p[0] = [p[1]]
#     else:
#         p[0] = p[1] + p[2]


def p_texts(p):
    '''texts : text_statement
             | texts text_statement'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + p[2]


def p_decl_text(p):
    '''decl_text : '.' TEXT
                 | '.' TEXT NUMBER'''

    global cur_text_addr
    if len(p) == 3:
        p[0] = []
        cur_text_addr = text_offset
    else:
        p[0] = ['0' * 32] * (p[3] / 4 - cur_text_addr)
        cur_text_addr = text_offset + p[3] / 4


def p_text_statement(p):
    '''text_statement : decl_text instructions'''
    p[0] = p[1] + p[2]


def p_instructions(p):
    '''instructions : instruction
                    | instructions instruction'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]


def p_instruction(p):
    '''instruction  : instruction_r
                    | instruction_i
                    | instruction_j
                    | VARIABLE ':' instruction'''
    global cur_text_addr
    if len(p) == 2:
        p[0] = p[1]
        cur_text_addr += 1
    else:
        p[0] = p[3]
        label_set[p[1]] = (cur_text_addr - 1) * 4


def p_expression(p):
    '''expression : NUMBER
                  | '-' NUMBER
                  | VARIABLE'''
    if len(p) == 3:
        p[0] = -p[2]
    elif type(p[1]) == str:
        p[0] = '##%s##' % p[1]
    else:
        p[0] = p[1]


def p_instruction_r(p):
    '''instruction_r : instruction_add
                    | instruction_addu
                    | instruction_sub
                    | instruction_subu
                    | instruction_and
                    | instruction_mult
                    | instruction_multu
                    | instruction_div
                    | instruction_divu
                    | instruction_mfhi
                    | instruction_mflo
                    | instruction_mthi
                    | instruction_mtlo
                    | instruction_mfc0
                    | instruction_mtc0
                    | instruction_or
                    | instruction_xor
                    | instruction_nor
                    | instruction_slt
                    | instruction_sltu
                    | instruction_sll
                    | instruction_srl
                    | instruction_sra
                    | instruction_sllv
                    | instruction_srlv
                    | instruction_srav
                    | instruction_jr
                    | instruction_jalr
                    | instruction_break
                    | instruction_syscall
                    | instruction_eret'''
    p[0] = p[1]


def p_instruction_add(p):
    "instruction_add : ADD REG REG REG"
    p[0] = op[p[1]] + reg_num[p[3]] + reg_num[p[4]] + reg_num[p[2]] + '0' * 5 + func[p[1]]


def p_instruction_addu(p):
    "instruction_addu : ADDU REG REG REG"
    p[0] = op[p[1]] + reg_num[p[3]] + reg_num[p[4]] + reg_num[p[2]] + '0' * 5 + func[p[1]]


def p_instruction_sub(p):
    "instruction_sub : SUB REG REG REG"
    p[0] = op[p[1]] + reg_num[p[3]] + reg_num[p[4]] + reg_num[p[2]] + '0' * 5 + func[p[1]]


def p_instruction_subu(p):
    "instruction_subu : SUBU REG REG REG"
    p[0] = op[p[1]] + reg_num[p[3]] + reg_num[p[4]] + reg_num[p[2]] + '0' * 5 + func[p[1]]


def p_instruction_and(p):
    "instruction_and : AND REG REG REG"
    p[0] = op[p[1]] + reg_num[p[3]] + reg_num[p[4]] + reg_num[p[2]] + '0' * 5 + func[p[1]]


def p_instruction_mult(p):
    "instruction_mult : MULT REG REG"
    p[0] = op[p[1]] + reg_num[p[2]] + reg_num[p[3]] + '0' * 10 + func[p[1]]


def p_instruction_multu(p):
    "instruction_multu : MULTU REG REG"
    p[0] = op[p[1]] + reg_num[p[2]] + reg_num[p[3]] + '0' * 10 + func[p[1]]


def p_instruction_div(p):
    "instruction_div : DIV REG REG"
    p[0] = op[p[1]] + reg_num[p[2]] + reg_num[p[3]] + '0' * 10 + func[p[1]]


def p_instruction_divu(p):
    "instruction_divu : DIVU REG REG"
    p[0] = op[p[1]] + reg_num[p[2]] + reg_num[p[3]] + '0' * 10 + func[p[1]]


def p_instruction_mfhi(p):
    "instruction_mfhi : MFHI REG"
    p[0] = op[p[1]] + '0' * 10 + reg_num[p[2]] + '0' * 5 + func[p[1]]


def p_instruction_mflo(p):
    "instruction_mflo : MFLO REG"
    p[0] = op[p[1]] + '0' * 10 + reg_num[p[2]] + '0' * 5 + func[p[1]]


def p_instruction_mthi(p):
    "instruction_mthi : MTHI REG"
    p[0] = op[p[1]] + reg_num[p[2]] + '0' * 15 + func[p[1]]


def p_instruction_mtlo(p):
    "instruction_mtlo : MTLO REG"
    p[0] = op[p[1]] + reg_num[p[2]] + '0' * 15 + func[p[1]]


def p_instruction_mfc0(p):
    "instruction_mfc0 : MFC0 REG REG expression"
    p[0] = op[p[1]] + '0' * 5 + reg_num[p[2]] + reg_num[p[3]] + '0' * 8 + '{0:03b}'.format(p[4])


def p_instruction_mtc0(p):
    "instruction_mtc0 : MTC0 REG REG expression"
    p[0] = op[p[1]] + '00100' + reg_num[p[2]] + reg_num[p[3]] + '0' * 8 + '{0:03b}'.format(p[4])


def p_instruction_or(p):
    "instruction_or : OR REG REG REG"
    p[0] = op[p[1]] + reg_num[p[3]] + reg_num[p[4]] + reg_num[p[2]] + '0' * 5 + func[p[1]]


def p_instruction_xor(p):
    "instruction_xor : XOR REG REG REG"
    p[0] = op[p[1]] + reg_num[p[3]] + reg_num[p[4]] + reg_num[p[2]] + '0' * 5 + func[p[1]]


def p_instruction_nor(p):
    "instruction_nor : NOR REG REG REG"
    p[0] = op[p[1]] + reg_num[p[3]] + reg_num[p[4]] + reg_num[p[2]] + '0' * 5 + func[p[1]]


def p_instruction_slt(p):
    "instruction_slt : SLT REG REG REG"
    p[0] = op[p[1]] + reg_num[p[3]] + reg_num[p[4]] + reg_num[p[2]] + '0' * 5 + func[p[1]]


def p_instruction_sltu(p):
    "instruction_sltu : SLTU REG REG REG"
    p[0] = op[p[1]] + reg_num[p[3]] + reg_num[p[4]] + reg_num[p[2]] + '0' * 5 + func[p[1]]


def p_instruction_sll(p):
    "instruction_sll : SLL REG REG expression"
    p[0] = op[p[1]] + '0' * 5 + reg_num[p[3]] + reg_num[p[2]] + '{0:05b}'.format(p[4]) + func[p[1]]


def p_instruction_srl(p):
    "instruction_srl : SRL REG REG expression"
    p[0] = op[p[1]] + '0' * 5 + reg_num[p[3]] + reg_num[p[2]] + '{0:05b}'.format(p[4]) + func[p[1]]


def p_instruction_sra(p):
    "instruction_sra : SRA REG REG expression"
    p[0] = op[p[1]] + '0' * 5 + reg_num[p[3]] + reg_num[p[2]] + '{0:05b}'.format(p[4]) + func[p[1]]


def p_instruction_sllv(p):
    "instruction_sllv : SLLV REG REG REG"
    p[0] = op[p[1]] + reg_num[p[4]] + reg_num[p[3]] + reg_num[p[2]] + '0' * 5 + func[p[1]]


def p_instruction_srlv(p):
    "instruction_srlv : SRLV REG REG REG"
    p[0] = op[p[1]] + reg_num[p[4]] + reg_num[p[3]] + reg_num[p[2]] + '0' * 5 + func[p[1]]


def p_instruction_srav(p):
    "instruction_srav : SRAV REG REG REG"
    p[0] = op[p[1]] + reg_num[p[4]] + reg_num[p[3]] + reg_num[p[2]] + '0' * 5 + func[p[1]]


def p_instruction_jr(p):
    "instruction_jr : JR REG"
    p[0] = op[p[1]] + reg_num[p[2]] + '0' * 15 + func[p[1]]


def p_instruction_jalr(p):
    "instruction_jalr : JALR REG REG"
    p[0] = op[p[1]] + reg_num[p[3]] + '0' * 5 + reg_num[p[2]] + '0' * 5 + func[p[1]]


def p_instruction_break(p):
    "instruction_break : BREAK"
    p[0] = op[p[1]] + '0' * 20 + func[p[1]]


def p_instruction_syscall(p):
    "instruction_syscall : SYSCALL"
    p[0] = op[p[1]] + '0' * 20 + func[p[1]]


def p_instruction_eret(p):
    "instruction_eret : ERET"
    p[0] = op[p[1]] + '1' + '0' * 19 + func[p[1]]


def p_instruction_i(p):
    '''instruction_i : instruction_addi
                    | instruction_addiu
                    | instruction_andi
                    | instruction_ori
                    | instruction_xori
                    | instruction_lui
                    | instruction_lb
                    | instruction_lbu
                    | instruction_lh
                    | instruction_lhu
                    | instruction_sb
                    | instruction_sh
                    | instruction_lw
                    | instruction_sw
                    | instruction_beq
                    | instruction_bne
                    | instruction_bgez
                    | instruction_bgtz
                    | instruction_blez
                    | instruction_bltz
                    | instruction_bgezal
                    | instruction_bltzal
                    | instruction_slti
                    | instruction_sltiu'''
    p[0] = p[1]


def p_instruction_addi(p):
    "instruction_addi : ADDI REG REG expression"
    p[0] = op[p[1]] + reg_num[p[3]] + reg_num[p[2]] + extend_16(p[4])


def p_instruction_addiu(p):
    "instruction_addiu : ADDIU REG REG expression"
    p[0] = op[p[1]] + reg_num[p[3]] + reg_num[p[2]] + extend_16(p[4])


def p_instruction_andi(p):
    "instruction_andi : ANDI REG REG expression"
    p[0] = op[p[1]] + reg_num[p[3]] + reg_num[p[2]] + extend_16(p[4])


def p_instruction_ori(p):
    "instruction_ori : ORI REG REG expression"
    p[0] = op[p[1]] + reg_num[p[3]] + reg_num[p[2]] + extend_16(p[4])


def p_instruction_xori(p):
    "instruction_xori : XORI REG REG expression"
    p[0] = op[p[1]] + reg_num[p[3]] + reg_num[p[2]] + extend_16(p[4])


def p_instruction_lui(p):
    "instruction_lui : LUI REG expression"
    p[0] = op[p[1]] + '0' * 5 + reg_num[p[2]] + extend_16(p[3])


def p_instruction_lb(p):
    "instruction_lb : LB REG expression '(' REG ')'"
    p[0] = op[p[1]] + reg_num[p[5]] + reg_num[p[2]] + extend_16(p[3])


def p_instruction_lbu(p):
    "instruction_lbu : LBU REG expression '(' REG ')'"
    p[0] = op[p[1]] + reg_num[p[5]] + reg_num[p[2]] + extend_16(p[3])


def p_instruction_lh(p):
    "instruction_lh : LH REG expression '(' REG ')'"
    p[0] = op[p[1]] + reg_num[p[5]] + reg_num[p[2]] + extend_16(p[3])


def p_instruction_lhu(p):
    "instruction_lhu : LHU REG expression '(' REG ')'"
    p[0] = op[p[1]] + reg_num[p[5]] + reg_num[p[2]] + extend_16(p[3])


def p_instruction_sb(p):
    "instruction_sb : SB REG expression '(' REG ')'"
    p[0] = op[p[1]] + reg_num[p[5]] + reg_num[p[2]] + extend_16(p[3])


def p_instruction_sh(p):
    "instruction_sh : SH REG expression '(' REG ')'"
    p[0] = op[p[1]] + reg_num[p[5]] + reg_num[p[2]] + extend_16(p[3])


def p_instruction_lw(p):
    "instruction_lw : LW REG expression '(' REG ')'"
    p[0] = op[p[1]] + reg_num[p[5]] + reg_num[p[2]] + extend_16(p[3])


def p_instruction_sw(p):
    "instruction_sw : SW REG expression '(' REG ')'"
    p[0] = op[p[1]] + reg_num[p[5]] + reg_num[p[2]] + extend_16(p[3])


def p_instruction_beq(p):
    "instruction_beq : BEQ REG REG expression"
    if type(p[4]) == int:
        p[0] = op[p[1]] + reg_num[p[2]] + reg_num[p[3]] + extend_16(p[4])
    else:
        p[0] = op[p[1]] + reg_num[p[2]] + reg_num[p[3]] + '!!%s!!' % p[4][2:-2]


def p_instruction_bne(p):
    "instruction_bne : BNE REG REG expression"
    if type(p[4]) == int:
        p[0] = op[p[1]] + reg_num[p[2]] + reg_num[p[3]] + extend_16(p[4])
    else:
        p[0] = op[p[1]] + reg_num[p[2]] + reg_num[p[3]] + '!!%s!!' % p[4][2:-2]


def p_instruction_bgez(p):
    "instruction_bgez : BGEZ REG expression"
    p[0] = op[p[1]] + reg_num[p[2]] + '00001' + extend_16(p[3])


def p_instruction_bgtz(p):
    "instruction_bgtz : BGTZ REG expression"
    p[0] = op[p[1]] + reg_num[p[2]] + '00000' + extend_16(p[3])


def p_instruction_blez(p):
    "instruction_blez : BLEZ REG expression"
    p[0] = op[p[1]] + reg_num[p[2]] + '00000' + extend_16(p[3])


def p_instruction_bltz(p):
    "instruction_bltz : BLTZ REG expression"
    p[0] = op[p[1]] + reg_num[p[2]] + '00000' + extend_16(p[3])


def p_instruction_bgezal(p):
    "instruction_bgezal : BGEZAL REG expression"
    p[0] = op[p[1]] + reg_num[p[2]] + '10001' + extend_16(p[3])


def p_instruction_bltzal(p):
    "instruction_bltzal : BLTZAL REG expression"
    p[0] = op[p[1]] + reg_num[p[2]] + '10000' + extend_16(p[3])


def p_instruction_slti(p):
    "instruction_slti : SLTI REG REG expression"
    p[0] = op[p[1]] + reg_num[p[3]] + reg_num[p[2]] + extend_16(p[4])


def p_instruction_sltiu(p):
    "instruction_sltiu : SLTIU REG REG expression"
    p[0] = op[p[1]] + reg_num[p[3]] + reg_num[p[2]] + extend_16(p[4])


def p_instruction_j(p):
    '''instruction_j : instruction_jj
                    | instruction_jal'''
    p[0] = p[1]


def p_instruction_jj(p):
    "instruction_jj : J expression"
    if type(p[2]) == int:
        p[0] = op[p[1]] + extend_26(p[2] / 4)
    else:
        p[0] = op[p[1]] + "&&%s&&" % p[2][2:-2]


def p_instruction_jal(p):
    "instruction_jal : JAL expression"
    if type(p[2]) == int:
        p[0] = op[p[1]] + extend_26(p[2] / 4)
    else:
        p[0] = op[p[1]] + "&&%s&&" % p[2][2:-2]


def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")

    global names, data_offset, cur_data_addr, cur_text_addr, data_memory_set, label_set

    names = {}
    data_offset = 0
    cur_data_addr = 0  # has been divided by 4
    cur_text_addr = 0  # has been divided by 4

    data_memory_set = {}  # key: addr; value: data, and this addr is real addr
    label_set = {}  # key: label_name; value: addr, and this addr is real addr
