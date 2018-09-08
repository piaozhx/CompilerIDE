# -*- coding: utf-8 -*-
# @Time    : 2016/12/20 上午10:35
# @Author  : Zhixin Piao 
# @Email   : piaozhx@seu.edu.cn


def sp_init(addr):
    return ["ori $sp, $0, %s" % addr]


def sp_push(reg_name):
    return ["sw %s, 0 ($sp)" % reg_name,
            "addi $sp, $sp, 4"]


def sp_pop(reg_name):
    return ["addi $sp, $sp, -4",
            "lw %s, 0 ($sp)" % reg_name]


class RegManager:
    # $0 - forever return 0;
    # $31 - save return address;
    # $26 / $27 intereption / exception
    # $24 / $25 save temp value
    # $29 --> $sp
    global_reg = ['$1', '$8', '$9', '$10', '$11', '$12', '$13', '$14', '$15', '$28', '$30']
    param_reg = ['$4', '$5', '$6', '$7']
    local_reg = ['$16', '$17', '$18', '$19', '$20', '$21', '$22', '$23']
    return_reg = ['$2', '$3']
    stack_idxs = []
    index_g_reg = 0
    index_l_reg = 0
    index_p_reg = 0

    global_var_reg_map = {}
    local_var_reg_map = {}

    def __init__(self):
        pass

    def get_reg(self, name):
        if name in self.global_var_reg_map.keys():
            return self.global_var_reg_map[name]
        else:
            return self.local_var_reg_map[name]

    def set_var(self, name, var_type='local'):
        if var_type == 'global':
            self.global_var_reg_map[name] = self.get_new_reg(reg_type=var_type)
            return self.global_var_reg_map[name]
        else:
            self.local_var_reg_map[name] = self.get_new_reg(reg_type=var_type)
            return self.local_var_reg_map[name]

    # get param from param_reg to local_reg
    # return instructions
    def get_param(self, name):
        self.local_var_reg_map[name] = self.get_new_reg(reg_type="local")
        p_reg = self.param_reg[self.index_l_reg - 1]
        return ["or %s, $0, %s" % (self.local_var_reg_map[name], p_reg)]

    # set param to param_reg
    # return reg_name
    def set_param(self):
        return self.get_new_reg(reg_type="param")

    # get new reg which either global reg or local reg
    # Reg-Type: param, local, global
    def get_new_reg(self, reg_type='local'):
        if reg_type == 'local':
            self.index_l_reg += 1
            return self.local_reg[self.index_l_reg - 1]
        elif reg_type == 'global':
            self.index_g_reg += 1
            return self.global_reg[self.index_g_reg - 1]
        elif reg_type == 'param':
            self.index_p_reg += 1
            return self.param_reg[self.index_p_reg - 1]

    # it is the 1st thing to do for calling function
    def save_local_reg(self):
        self.stack_idxs += [self.index_l_reg, self.index_p_reg, self.local_var_reg_map]
        self.index_l_reg = 0
        self.index_p_reg = 0
        self.local_var_reg_map = {}
        return self.push_all()

    def reset_local_reg(self):
        self.local_var_reg_map = self.stack_idxs.pop()
        self.index_p_reg = self.stack_idxs.pop()
        self.index_l_reg = self.stack_idxs.pop()

        return self.pop_all()

    def clean_local_reg(self):
        self.local_var_reg_map = {}
        self.index_l_reg = 0

    def clean_param_reg(self):
        self.index_p_reg = 0

    def get_return_reg(self, num=1):
        if num == 1:
            return self.return_reg[0]
        else:
            return self.return_reg

    def get_reg_by_idx(self, idx, reg_type='local'):
        if reg_type == 'global':
            return self.global_reg[idx]
        elif reg_type == 'local':
            return self.local_reg[idx]
        else:
            return self.param_reg[idx]

    def push_all(self):
        ins = []
        for reg in self.local_reg + self.param_reg + ['$31']:
            ins += sp_push(reg)
        return ins

    def pop_all(self):
        ins = []
        for reg in (self.local_reg + self.param_reg + ['$31'])[::-1]:
            ins += sp_pop(reg)
        return ins
