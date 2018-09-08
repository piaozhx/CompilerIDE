# -*- coding: utf-8 -*-
# @Time    : 2016/12/19 上午10:19
# @Author  : Zhixin Piao 
# @Email   : piaozhx@seu.edu.cn

# Parsing rules
# 如果code不是从0开始的那么会有很严重的问题
from reg_manager import RegManager, sp_init

names = {}
interrupt_ins = []
reg_manager = RegManager()
res_code = ['']
loop_num = 0
if_num = 0

precedence = (
    ('nonassoc', 'EQ', 'NE', 'LE', 'GE', 'LT', 'GT'),  # Nonassociative operators
    ('left', 'AND', 'OR'),
    ('left', '+', '-'),
    ('left', '|'),
    ('left', '&', '^'),
    ('left', '*', '/', '%'),
    ('left', 'LSHIFT', 'RSHIFT'),
    ('right', '!'),
    ('right', '~'),
    ('right', '$'),
    ('right', 'UMINUS'),  # Unary minus operator
    ('nonassoc', 'PELSE')  # 解决if-else冲突
)


def main(codes):
    global names, reg_manager, loop_num, if_num, interrupt_ins, res_code

    res_code[0] = '.DATA\n'
    for code in codes['data']:
        res_code[0] += '%s\n' % code

    res_code[0] += '.TEXT\n'
    for code in codes['text']:
        res_code[0] += '%s\n' % code

    names = {}
    interrupt_ins = []
    reg_manager = RegManager()
    loop_num = 0
    if_num = 0


# 最开始要在某个内存初始化sp
def p_start(p):
    'start : program'
    p[0] = {'data': [], 'text': []}
    p[0]['text'] = ["beq $0, $0, 2", "or $0, $0, $0", "or $0, $0, $0"]
    p[0]['text'] += sp_init(4000)
    p[0]['text'] += p[1]
    p[0]['data'] = interrupt_ins

    main(p[0])


# 程序由变量描述或函数描述组成(decl)
def p_program(p):
    'program : decl_list'
    p[0] = p[1]


def p_decl_list(p):
    '''decl_list : decl
                 | decl_list decl'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + p[2]


def p_decl(p):
    '''decl : var_decl
            | fun_decl'''
    p[0] = p[1]


# 变量包括简单变量和一维数组变量
def p_var_decl(p):
    '''var_decl : type_spec VARIABLE ';'
                | type_spec VARIABLE '[' NUMBER ']' ';' '''

    if len(p) == 4:
        p[0] = ["ori %s, $0, 0" % reg_manager.set_var(p[2], var_type="global")]


def p_type_spec(p):
    '''type_spec : VOID
                 | INT'''


# 要考虑设置全局函数信息
def p_fun_decl(p):
    '''fun_decl : type_spec VARIABLE '(' params ')' compound_stmt
                | type_spec VARIABLE '(' params ')' ';' '''
    if p[6] != ';':
        if p[2].find('interrupt') == -1:
            p[0] = ["j %s_end" % p[2]] if p[2] != 'main' else []
            p[0] += ['%s:' % p[2]]
            p[0] += p[4]
            p[0] += p[6]
            p[0] += ["jr $31", "%s_end:" % p[2], "beq $0, $0, 0"]
        else:
            global interrupt_ins
            p[0] = ["j %s_end" % p[2]]
            p[0] += ['%s:' % p[2]]
            p[0] += reg_manager.save_local_reg()
            p[0] += p[6]
            p[0] += reg_manager.reset_local_reg()
            p[0] += ["eret", "%s_end:" % p[2], "beq $0, $0, 0"]

            offset = int(p[2][p[2].find('_') + 1:])
            # interrupt_ins += ["ori $24, $0, %s" % p[2], "sw $24, %d($0)" % (offset * 4)]
            interrupt_ins += ["func_%s: .word %s" % (p[2], p[2])]

        reg_manager.clean_local_reg()


# 函数参数个数可为0或多个
def p_params(p):
    '''params : param_list
              | VOID
              | empty'''
    if p[1] is None or p[1] == 'void':
        p[0] = []
    else:
        p[0] = p[1]


def p_param_list(p):
    '''param_list : param
                  | param_list ',' param'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + p[3]


def p_param(p):
    '''param : type_spec VARIABLE
             | type_spec VARIABLE '[' NUMBER ']' '''
    if len(p) == 3:
        p[0] = reg_manager.get_param(p[2])


def p_stmt_list(p):
    '''stmt_list : stmt_list stmt
                 | empty'''
    if len(p) == 3:
        if p[1] is not None:
            p[0] = p[1] + p[2]
        else:
            p[0] = p[2]


def p_stmt(p):
    '''stmt : expr_stmt
            | block_stmt
            | if_stmt
            | while_stmt
            | return_stmt
            | continue_stmt
            | break_stmt
            | eret_stmt'''
    p[0] = p[1]


def p_eret_stmt(p):
    "eret_stmt : ERET ';' "
    p[0] = ["eret"]


# 赋值语句
# expr在非数字情况下应存储该值寄存器的名字
def p_expr_stmt(p):
    '''expr_stmt : VARIABLE '=' expr ';'
              | VARIABLE '[' expr ']' '=' expr ';'
              | '$' expr '=' expr ';'
              | expr ';' '''

    if p[2] == '=':
        # p[3]的val要么是数字，要么是寄存器, ins是指令
        p[0] = p[3]["ins"]
        if type(p[3]["val"]) == int:
            p[0] += ["ori %s, $0, %d" % (reg_manager.get_reg(p[1]), p[3]["val"])]
        else:
            p[0] += ["or %s, $0, %s" % (reg_manager.get_reg(p[1]), p[3]["val"])]
    elif p[2] == '[':
        # p[3], p[6]的val要么是数字，要么是寄存器, ins是指令
        p[0] = p[3]["ins"] + p[6]["ins"]
        if type(p[3]["val"]) == int:
            if type(p[6]["val"]) == int:
                p[0] += ["ori %s, $0, %d" % ("$24", p[6]["val"]),
                         "sw %s, %d (%s)" % ("$24", p[3]["val"], reg_manager.get_reg(p[1]))]
            else:
                p[0] += ["sw %s, %d (%s)" % (p[6]["val"], p[3]["val"], reg_manager.get_reg(p[1]))]
        else:
            if type(p[6]["val"]) == int:
                p[0] += ["ori %s, $0, %d" % ("$24", p[6]["val"]),
                         "add %s, %s, %s" % ("$25", p[3]["val"], reg_manager.get_reg(p[1])),
                         "sw %s, %d (%s)" % ("$24", 0, "$25")]
            else:
                p[0] += ["add %s, %s, %s" % ("$25", p[3]["val"], reg_manager.get_reg(p[1])),
                         "sw %s, %d (%s)" % (p[6]["val"], 0, "$25")]
    elif p[1] == '$':
        # p[2], p[4] 的val要么是数字，要么是寄存器, ins是指令
        p[0] = p[2]["ins"] + p[4]["ins"]
        if type(p[2]["val"]) == int:
            if type(p[4]["val"]) == int:
                p[0] += ["ori %s, $0, %d" % ("$24", p[4]["val"]),
                         "sw %s, %d ($0)" % ("$24", p[2]["val"])]
            else:
                p[0] += ["sw %s, %d ($0)" % (p[4]["val"], p[2]["val"])]
        else:
            if type(p[4]["val"]) == int:
                p[0] += ["ori %s, $0, %d" % ("$24", p[4]["val"]),
                         "sw %s, 0 (%s)" % ("$24", p[2]["val"])]
            else:
                p[0] += ["sw %s, 0 (%s)" % (p[4]["val"], p[2]["val"])]
    else:
        p[0] = p[1]["ins"]


# while 语句
def p_while_stmt(p):
    "while_stmt : WHILE '(' expr ')' stmt"
    # p[3]的val要么是数字，要么是寄存器, ins是指令
    global loop_num

    p[0] = p[3]["ins"]
    if type(p[3]["val"]) == int:
        p[0] += ["ori %s, $0, %d" % ("$24", p[3]["val"]),
                 "start_loop%d:" % loop_num,
                 "bne %s, $0, 1" % "$24"]
    else:
        p[0] += ["start_loop%d:" % loop_num,
                 "bne %s, $0, 1" % p[3]["val"]]
    p[0] += ["j end_loop%d" % loop_num] + p[5] + ["j start_loop%d" % loop_num, "end_loop%d:" % loop_num]
    loop_num += 1


# 语句块
def p_block_stmt(p):
    "block_stmt : '{' stmt_list '}'"
    p[0] = p[2]


# 函数内部描述，包括局部变量和语句描述
def p_compound_stmt(p):
    "compound_stmt : '{' local_decls stmt_list '}'"
    p[0] = p[2] + p[3]


# 函数内部变量描述
def p_local_decls(p):
    '''local_decls : local_decls local_decl
                   | empty '''
    if len(p) == 2:
        p[0] = []
    else:
        p[0] = p[1] + p[2]


def p_local_decl(p):
    '''local_decl : type_spec VARIABLE ';'
                  | type_spec VARIABLE '[' NUMBER ']' ';' '''
    if len(p) == 4:
        p[0] = ["ori %s, $0, 0" % reg_manager.set_var(p[2], var_type="local")]


# 这个要注意一下
def p_if_stmt(p):
    '''if_stmt : IF '(' expr ')' stmt
               | IF '(' expr ')' stmt ELSE stmt %prec PELSE'''

    global if_num
    p[0] = p[3]["ins"]
    if type(p[3]["val"]) == int:
        p[0] += ["ori %s, $0, %d" % ("$24", p[3]["val"]),
                 "bne %s, $0, 1" % "$24"]
    else:
        p[0] += ["bne %s, $0, 1" % p[3]["val"]]

    if len(p) == 6:
        p[0] += ["j end_if%d" % if_num, "j start_if%d" % if_num]
        p[0] += ["start_if%d:" % if_num] + p[5] + ["end_if%d:" % if_num]
    else:
        p[0] += ["j start_else%d" % if_num, "j start_if%d" % if_num]
        p[0] += ["start_if%d:" % if_num] + p[5] + ["j end_if%d" % if_num]
        p[0] += ["start_else%d:" % if_num] + p[7] + ["end_if%d:" % if_num]

    if_num += 1


def p_return_stmt(p):
    '''return_stmt : RETURN ';'
                   | RETURN expr ';' '''
    if len(p) == 3:
        p[0] = ["jr $31"]


def p_expr(p):
    '''expr : expr OR expr
            | expr AND expr
            | expr EQ expr
            | expr NE expr
            | expr LE expr
            | expr LT expr
            | expr GE expr
            | expr GT expr
            | expr '*' expr
            | expr '/' expr
            | expr '%' expr
            | expr '+' expr
            | expr '-' expr
            | expr '&' expr
            | expr '^' expr
            | expr '|' expr
            | expr LSHIFT expr
            | expr RSHIFT expr'''

    res = {"ins": p[1]["ins"] + p[3]["ins"]}
    # 逻辑或功能
    if p[2] == '||':
        if type(p[1]["val"]) == int:
            if type(p[3]["val"]) == int:
                res["val"] = p[1]["val"] or p[3]["val"]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["ori %s, %s, %d" % (res["val"], p[3]["val"], p[1]["val"]),
                               "sltu %s, $0, %s" % (res["val"], res["val"])]
        else:
            if type(p[3]["val"]) == int:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["ori %s, %s, %d" % (res["val"], p[1]["val"], p[3]["val"]),
                               "sltu %s, $0, %s" % (res["val"], res["val"])]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["or %s, %s, %s" % (res["val"], p[1]["val"], p[3]["val"]),
                               "sltu %s, $0, %s" % (res["val"], res["val"])]

    # 逻辑与功能
    elif p[2] == '&&':
        if type(p[1]["val"]) == int:
            if type(p[3]["val"]) == int:
                res["val"] = p[1]["val"] and p[3]["val"]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["sltu %s, $0, %s" % ("$24", p[3]["val"]),
                               "sltiu %s, $0, %d" % ("$25", p[1]["val"]),
                               "and %s, %s, %s" % (res["val"], "$24", "$25"),
                               "sltu %s, $0, %s" % (res["val"], res["val"])]
        else:
            if type(p[3]["val"]) == int:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["sltu %s, $0, %s" % ("$24", p[1]["val"]),
                               "sltiu %s, $0, %d" % ("$25", p[3]["val"]),
                               "and %s, %s, %s" % (res["val"], "$24", "$25"),
                               "sltu %s, $0, %s" % (res["val"], res["val"])]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["sltu %s, $0, %s" % ("$24", p[3]["val"]),
                               "sltu %s, $0, %s" % ("$25", p[1]["val"]),
                               "and %s, %s, %s" % (res["val"], "$24", "$25"),
                               "sltu %s, $0, %s" % (res["val"], res["val"])]

    # 逻辑等功能:
    elif p[2] == '==':
        if type(p[1]["val"]) == int:
            if type(p[3]["val"]) == int:
                res["val"] = p[1]["val"] == p[3]["val"]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["xori %s, %s, %d" % (res["val"], p[3]["val"], p[1]["val"]),
                               "sltu %s, $0, %s" % (res["val"], res["val"]),
                               "xori %s, %s, %d" % (res["val"], res["val"], 1)]
        else:
            if type(p[3]["val"]) == int:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["xori %s, %s, %d" % (res["val"], p[1]["val"], p[3]["val"]),
                               "sltu %s, $0, %s" % (res["val"], res["val"]),
                               "xori %s, %s, %d" % (res["val"], res["val"], 1)]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["xor %s, %s, %s" % (res["val"], p[1]["val"], p[3]["val"]),
                               "sltu %s, $0, %s" % (res["val"], res["val"]),
                               "xori %s, %s, %d" % (res["val"], res["val"], 1)]

    # 逻辑不等功能
    elif p[2] == '!=':
        if type(p[1]["val"]) == int:
            if type(p[3]["val"]) == int:
                res["val"] = p[1]["val"] != p[3]["val"]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["xori %s, %s, %d" % (res["val"], p[3]["val"], p[1]["val"]),
                               "sltu %s, %s, $0" % (res["val"], res["val"])]
        else:
            if type(p[3]["val"]) == int:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["xori %s, %s, %d" % (res["val"], p[1]["val"], p[3]["val"]),
                               "sltu %s, %s, $0" % (res["val"], res["val"])]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["xor %s, %s, %s" % (res["val"], p[1]["val"], p[3]["val"]),
                               "sltu %s, %s, $0" % (res["val"], res["val"])]

    # 小于等于功能
    elif p[2] == '<=':
        if type(p[1]["val"]) == int:
            if type(p[3]["val"]) == int:
                res["val"] = p[1]["val"] <= p[3]["val"]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["slti %s, %s, %d" % (res["val"], p[3]["val"], p[1]["val"]),
                               "xori %s, %s, %d" % (res["val"], res["val"], 1)]
        else:
            if type(p[3]["val"]) == int:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["ori %s, $0, %d" % ("$24", p[3]["val"]),
                               "slt %s, %s, %s" % (res["val"], "$24", p[1]["val"]),
                               "xori %s, %s, %d" % (res["val"], res["val"], 1)]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["slt %s, %s, %s" % (res["val"], p[3]["val"], p[1]["val"]),
                               "xori %s, %s, %d" % (res["val"], res["val"], 1)]

    # 大于等于功能
    elif p[2] == '>=':
        if type(p[1]["val"]) == int:
            if type(p[3]["val"]) == int:
                res["val"] = p[1]["val"] >= p[3]["val"]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["ori %s, $0, %d" % ("$24", p[1]["val"]),
                               "slt %s, %s, %s" % (res["val"], "$24", p[3]["val"]),
                               "xori %s, %s, %d" % (res["val"], res["val"], 1)]
        else:
            if type(p[3]["val"]) == int:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["slti %s, %s, %d" % (res["val"], p[1]["val"], p[3]["val"]),
                               "xori %s, %s, %d" % (res["val"], res["val"], 1)]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["slt %s, %s, %s" % (res["val"], p[1]["val"], p[3]["val"]),
                               "xori %s, %s, %d" % (res["val"], res["val"], 1)]

    # 大于功能
    elif p[2] == '>':
        if type(p[1]["val"]) == int:
            if type(p[3]["val"]) == int:
                res["val"] = p[1]["val"] > p[3]["val"]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["slti %s, %s, %d" % (res["val"], p[3]["val"], p[1]["val"])]
        else:
            if type(p[3]["val"]) == int:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["ori %s, $0, %d" % (res["val"], p[3]["val"]),
                               "slt %s, %s, %s" % (res["val"], res["val"], p[1]["val"])]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["slt %s, %s, %s" % (res["val"], p[3]["val"], p[1]["val"])]

    # 小于功能
    elif p[2] == '<':
        if type(p[1]["val"]) == int:
            if type(p[3]["val"]) == int:
                res["val"] = p[1]["val"] < p[3]["val"]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["ori %s, $0, %d" % (res["val"], p[1]["val"]),
                               "slt %s, %s, %s" % (res["val"], res["val"], p[3]["val"])]
        else:
            if type(p[3]["val"]) == int:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["slti %s, %s, %d" % (res["val"], p[1]["val"], p[3]["val"])]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["slt %s, %s, %s" % (res["val"], p[3]["val"], p[1]["val"])]

    # 按位或功能
    elif p[2] == '|':
        if type(p[1]["val"]) == int:
            if type(p[3]["val"]) == int:
                res["val"] = p[1]["val"] | p[3]["val"]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["ori %s, %s, %d" % (res["val"], p[3]["val"], p[1]["val"])]
        else:
            if type(p[3]["val"]) == int:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["ori %s, %s, %d" % (res["val"], p[1]["val"], p[3]["val"])]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["or %s, %s, %s" % (res["val"], p[1]["val"], p[3]["val"])]

    # 按位与功能
    elif p[2] == '&':
        if type(p[1]["val"]) == int:
            if type(p[3]["val"]) == int:
                res["val"] = p[1]["val"] & p[3]["val"]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["andi %s, %s, %d" % (res["val"], p[3]["val"], p[1]["val"])]
        else:
            if type(p[3]["val"]) == int:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["andi %s, %s, %d" % (res["val"], p[1]["val"], p[3]["val"])]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["and %s, %s, %s" % (res["val"], p[1]["val"], p[3]["val"])]

    # 按位异或功能
    elif p[2] == '^':
        if type(p[1]["val"]) == int:
            if type(p[3]["val"]) == int:
                res["val"] = p[1]["val"] ^ p[3]["val"]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["xori %s, %s, %d" % (res["val"], p[3]["val"], p[1]["val"])]
        else:
            if type(p[3]["val"]) == int:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["xori %s, %s, %d" % (res["val"], p[1]["val"], p[3]["val"])]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["xor %s, %s, %s" % (res["val"], p[1]["val"], p[3]["val"])]

    # 左移功能
    elif p[2] == '<<':
        if type(p[1]["val"]) == int:
            if type(p[3]["val"]) == int:
                res["val"] = p[1]["val"] << p[3]["val"]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["ori %s, $0, %d" % (res["val"], p[1]["val"]),
                               "sllv %s, %s, %s" % (res["val"], res["val"], p[3]["val"])]
        else:
            if type(p[3]["val"]) == int:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["sll %s, %s, %d" % (res["val"], p[1]["val"], p[3]["val"])]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["sllv %s, %s, %s" % (res["val"], p[1]["val"], p[3]["val"])]

    # 算数右移功能
    elif p[2] == '>>':
        if type(p[1]["val"]) == int:
            if type(p[3]["val"]) == int:
                res["val"] = p[1]["val"] >> p[3]["val"]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["ori %s, $0, %d" % (res["val"], p[1]["val"]),
                               "srav %s, %s, %s" % (res["val"], res["val"], p[3]["val"])]
        else:
            if type(p[3]["val"]) == int:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["sra %s, %s, %d" % (res["val"], p[1]["val"], p[3]["val"])]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["srav %s, %s, %s" % (res["val"], p[1]["val"], p[3]["val"])]

    # 加法功能
    elif p[2] == '+':
        if type(p[1]["val"]) == int:
            if type(p[3]["val"]) == int:
                res["val"] = p[1]["val"] + p[3]["val"]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["addi %s, %s, %d" % (res["val"], p[3]["val"], p[1]["val"])]
        else:
            if type(p[3]["val"]) == int:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["addi %s, %s, %d" % (res["val"], p[1]["val"], p[3]["val"])]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["add %s, %s, %s" % (res["val"], p[1]["val"], p[3]["val"])]

    # 减法功能
    elif p[2] == '-':
        if type(p[1]["val"]) == int:
            if type(p[3]["val"]) == int:
                res["val"] = p[1]["val"] - p[3]["val"]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["ori %s, $0, %d" % (res["val"], p[1]["val"]),
                               "sub %s, %s, %d" % (res["val"], res["val"], p[1]["val"])]
        else:
            if type(p[3]["val"]) == int:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["addi %s, %s, %d" % (res["val"], p[1]["val"], -p[3]["val"])]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["sub %s, %s, %s" % (res["val"], p[1]["val"], p[3]["val"])]

    # 乘法功能
    elif p[2] == '*':
        if type(p[1]["val"]) == int:
            if type(p[3]["val"]) == int:
                res["val"] = p[1]["val"] * p[3]["val"]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["ori %s, $0, %d" % (res["val"], p[1]["val"]),
                               "mult %s, %s" % (res["val"], p[3]["val"]),
                               "mflo %s" % res["val"]]
        else:
            if type(p[3]["val"]) == int:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["ori %s, $0, %d" % (res["val"], p[3]["val"]),
                               "mult %s, %s" % (res["val"], p[1]["val"]),
                               "mflo %s" % res["val"]]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["mult %s, %s" % (p[1]["val"], p[3]["val"]),
                               "mflo %s" % res["val"]]

    # 除法功能
    elif p[2] == '/':
        if type(p[1]["val"]) == int:
            if type(p[3]["val"]) == int:
                res["val"] = p[1]["val"] / p[3]["val"]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["ori %s, $0, %d" % (res["val"], p[1]["val"]),
                               "div %s, %s" % (res["val"], p[3]["val"]),
                               "mflo %s" % res["val"]]
        else:
            if type(p[3]["val"]) == int:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["ori %s, $0, %d" % (res["val"], p[3]["val"]),
                               "div %s, %s" % (p[1]["val"], res["val"]),
                               "mflo %s" % res["val"]]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["div %s, %s" % (p[1]["val"], p[3]["val"]),
                               "mflo %s" % res["val"]]

    # 取模功能
    elif p[2] == '%':
        if type(p[1]["val"]) == int:
            if type(p[3]["val"]) == int:
                res["val"] = p[1]["val"] / p[3]["val"]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["ori %s, $0, %d" % (res["val"], p[1]["val"]),
                               "div %s, %s" % (res["val"], p[3]["val"]),
                               "mfhi %s" % res["val"]]
        else:
            if type(p[3]["val"]) == int:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["ori %s, $0, %d" % (res["val"], p[3]["val"]),
                               "div %s, %s" % (p[1]["val"], res["val"]),
                               "mfhi %s" % res["val"]]
            else:
                res["val"] = reg_manager.get_new_reg()
                res["ins"] += ["div %s, %s" % (p[1]["val"], p[3]["val"]),
                               "mfhi %s" % res["val"]]

    p[0] = res


def p_expr_1(p):
    '''expr : '!' expr
            | '-' expr %prec UMINUS
            | '+' expr %prec UMINUS
            | '~' expr
            | '(' expr ')' '''

    res = {"ins": p[2]["ins"]}

    # 逻辑取反功能
    if p[1] == '!':
        if type(p[2]["val"]) == int:
            res["val"] = not p[2]["val"]
        else:
            res["val"] = reg_manager.get_new_reg()
            res["ins"] += ["slt %s, $0, %s" % (res["val"], p[2]["val"]),
                           "xori %s, %s, 1" % (res["val"], res["val"])]

    # 负数功能
    elif p[1] == '-':
        if type(p[2]["val"]) == int:
            res["val"] = - p[2]["val"]
        else:
            res["val"] = reg_manager.get_new_reg()
            res["ins"] += ["sub %s, $0, %s" % (res["val"], p[2]["val"])]

    # 正数功能
    elif p[1] == '+':
        res = p[2]

    # 按位取反功能
    elif p[1] == '~':
        if type(p[2]["val"]) == int:
            res["val"] = ~ p[2]["val"]
        else:
            res["val"] = reg_manager.get_new_reg()
            res["ins"] += ["nor %s, $0, %s" % (res["val"], p[2]["val"])]

    # 括号功能
    elif p[1] == '(':
        res = p[2]

    p[0] = res


def p_expr_0(p):
    '''expr : VARIABLE
            | NUMBER'''

    res = {}
    if type(p[1]) == str:
        res["val"] = reg_manager.get_reg(p[1])
        res["ins"] = []
    else:
        res["val"] = p[1]
        res["ins"] = []

    p[0] = res


# need add instrcution to get data from memory
# $ expr 为取端口地址为 expr 值的端口值
# VARIABLE ( args )为函数调用
def p_expr_data(p):
    '''expr : '$' expr
            | VARIABLE '[' expr ']'
            | VARIABLE '(' args ')' '''
    res = {}

    if p[2] == '(':
        # miniC 不支持函数赋值，保护现场是最先做的事情
        res["ins"] = reg_manager.save_local_reg()
        res["ins"] += p[3]
        res["ins"] += ["jal %s" % p[1]] + reg_manager.reset_local_reg()
        res["val"] = 0
    elif p[2] == '[':
        res["ins"] = p[3]["ins"]
        res["val"] = reg_manager.get_new_reg()

        if type(p[3]["val"]) == int:
            res["ins"] += ["sw %s, %d(%s)" % (res["val"], p[3]["val"], reg_manager.get_reg(p[1]))]
        else:
            res["ins"] += ["add %s, %s, %s" % ("$24", reg_manager.get_reg(p[1]), p[3]["val"]),
                           "sw %s, 0(%s)" % (res["val"], "$24")]
    else:
        res["ins"] = p[2]["ins"]
        res["val"] = reg_manager.get_new_reg()
        if type(p[2]["val"]) == int:
            res["ins"] += ["sw %s, %d($0)" % (res["val"], p[2]["val"])]
        else:
            res["ins"] += ["sw %s, 0(%s)" % (res["val"], p[2]["val"])]

    p[0] = res


# arg 要么为数字， 要么为寄存器名字
def p_args(p):
    '''args : arg_list
            | empty'''
    if p[1] is not None:
        p[0] = p[1]
        reg_manager.clean_param_reg()
    else:
        p[0] = []


def p_arg_list(p):
    '''arg_list : arg_list ',' expr
                | expr'''
    if len(p) == 2:
        p[0] = p[1]["ins"]
        if type(p[1]["val"]) == int:
            p[0] += ["ori %s, $0, %d" % (reg_manager.set_param(), p[1]["val"])]
        else:
            p[0] += ["or %s, $0, %s" % (reg_manager.set_param(), p[1]["val"])]
    else:
        p[0] = p[1] + p[3]["ins"]
        if type(p[3]["val"]) == int:
            p[0] += ["ori %s, $0, %d" % (reg_manager.set_param(), p[3]["val"])]
        else:
            p[0] += ["or %s, $0, %s" % (reg_manager.set_param(), p[3]["val"])]


def p_continue_stmt(p):
    "continue_stmt : CONTINUE ';'"
    p[0] = ["j start_loop%d" % loop_num]


def p_break_stmt(p):
    "break_stmt : BREAK ';'"
    p[0] = ["j end_loop%d" % loop_num]


def p_empty(p):
    'empty :'


def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")

    global names, reg_manager, loop_num, if_num, interrupt_ins, res_code

    names = {}
    interrupt_ins = []
    reg_manager = RegManager()
    loop_num = 0
    if_num = 0
