class Memory:
    def __init__(self):
        self.head = 100
        self.tmp_head = 1000
    
    def get_tmp(self):
        tmp = self.tmp_head
        self.tmp_head += 4
        return tmp
    
    def get_addr(self):
        return self.head
    
    def increase(self, count):
        self.head += 4 * count
    

class SymbolTable:
    def __init__(self, memory_manager):
        self.mm = memory_manager
        self.table = []
    
    def _initialize(self):
        self.add_function('output', 'void', {'return_addr': 50, 'code_addr': 1})
        self.add_variable('a', 'int', {'kind': 'param'})

    def add_variable(self, lexptr, type, attributes):
        addr = self.mm.get_addr()
        self.table.append({
            'lexptr': lexptr,
            'addr': addr,
            'type': type,
            'attr': attributes
        })
        if 'count' in attributes.keys():
            count = attributes['count']
        else:
            count = 1
        self.mm.increase(count)

    def add_function(self, lexptr, type, attributes):
        addr = self.mm.get_addr()
        attributes['return_addr'] = self.mm.get_tmp()
        self.table.append({
            'lexptr': lexptr,
            'addr': addr,
            'type': type,
            'attr': attributes
        })
        self.mm.increase(1)

    def get_by_addr(self, addr):
        flag = True
        for row in self.table[::-1]:
            if row['scope'] == 0:
                flag = False
                if row['addr'] == addr:
                    return row
            elif (flag and row['addr'] == addr):
                return row
        return None

    def get_by_name(self, name):
        flag = True
        for row in self.table[::-1]:
            if row['scope'] == 0:
                flag = False
                if row['lexeme'] == name:
                    return row
            elif (flag and row['lexeme'] == name):
                return row
        return None

    def get_index(self, name):
        flag = True
        for i, row in zip(range(len(self.table) - 1, -1, -1), self.table[::-1]):
            if row['scope'] == 0:
                flag = False
                if row['lexeme'] == name:
                    return i
            elif (flag and row['lexeme'] == name):
                return i
        return None


class CodeGenerator:

    def __init__(self):
        self.memory = Memory()
        self.ST = SymbolTable(self.memory)
        self.stack = []
        self.PB = []
        self.i = 0
        self.curr_param_count = 0
        self.curr_funcs_name = []
        self.curr_loops_name = []
        self._initialize()

    def _initialize(self):
        self.insert_code('(JP, 3, , )')
        self.insert_code('(PRINT, 104, , )')
        self.insert_code('(JP, @50, , )')

    def insert_code(self, code, i=None):
        if (i is None):
            self.PB.append(code)
            self.i += 1
        else:
            self.PB[i] = code

    def push(self, value):
        # todo: different push for num and other
        self.stack.append(value)

    def pop(self, n=1):
        for i in range(n):
            self.stack.pop()

    def save(self, lookahead):
        self.push(self.i)
        self.insert_code('')
        # self.i += 1

    def jpf_save(self, lookahead):
        self.insert_code(f'(JPF, {self.stack[-2]}, {self.i + 1}, )', i=self.stack[-1])
        self.pop(2)
        self.push(self.i)
        self.insert_code('')

    def jp(self, lookahead):
        self.insert_code(f'(JPF, {self.i}, , )', i=self.stack[-1])
        self.pop(1)

    def jpf(self, lookahead):
        self.insert_code(f'(JPF, {self.stack[-2]}, {self.i}, )', i=self.stack[-1])
        self.pop(2)

    def pid(self, lookahead):
        row = self.ST.get_by_name(lookahead)
        if row is None:
            #todo: handle semantic errors
            return
        else:
            self.push(row['addr'])
        
    def relop(self, lookahead):
        a, relop, b = self.stack[-3:]
        #todo: check type of a and b for semantic errors
        t = self.memory.get_tmp()
        if (relop == '=='):
            self.insert_code(f'(EQ, {a}, {b}, {t})')
        else:
            self.insert_code(f'(LT, {a}, {b}, {t})')
        self.pop(3)
        self.push(t)

    def add_sub(self, lookahead):
        a, op, b = self.stack[-3:]
        #todo: check type of a and b for semantic errors
        t = self.memory.get_tmp()
        if (op == '+'):
            self.insert_code(f'(ADD, {a}, {b}, {t})')
        else:
            self.insert_code(f'(SUB, {a}, {b}, {t})')
        self.pop(3)
        self.push(t)

    def mult(self, lookahead):
        a, b = self.stack[-2:]
        #todo: check type of a and b for semantic errors
        t = self.memory.get_tmp()
        self.insert_code(f'(MULT, {a}, {b}, {t})')
        self.pop(2)
        self.push(t)

    def assign(self, lookahead):
        b, a = self.stack[-2:]
        #todo: check type of a and b for semantic errors
        self.insert_code(f'(ASSIGN, {a}, {b})')
        self.pop(1)
    
    def get_arr(self, lookahead):
        t1 = self.memory.get_tmp()
        #todo: check t1 type
        self.insert_code(f'(MULT, {self.stack[-1]}, #4, {t1})')
        self.pop()
        t2 = self.memory.get_tmp()
        self.insert_code(f'(ADD, {t1}, {self.stack[-1], {t2}})')
        self.pop()
        self.push(f'@{t2}')

    def for_loop(self, lookahead):
        t = self.memory.get_tmp()
        self.curr_loops_name.append(t)
        self.push(t)
        self.push(self.i)
        self.insert_code('')

    def for_label(self, lookahead):
        self.push(self.i)
    
    def for_jpf(self, lookahead):
        self.push(self.i)
        self.insert_code('')
    
    def for_jmp(self, lookahead):
        t, for_begin, for_label, rel_op, for_jpf = self.stack[-5:]
        self.insert_code(f'(JP, {for_label}, , )')
        self.insert_code(f'(ASSIGN, #{self.i}, {t}, )', i=for_begin)
        self.insert_code(f'(JPF, {rel_op}, {self.i}, )', i=for_jpf)
        self.pop(5)
        self.curr_loops_name.pop()

    def break_loop(self, lookahead):
        t = self.curr_loops_name[-1]
        self.insert_code(f'(JP, @{t}, , )')
    
    def var_end(self, lookahead):
        if self.stack[-1].isnumeric():
            #array
            attr = {'count': self.stack[-1]}
            self.ST.add_variable(self.stack[-2], self.stack[-1], attributes=attr)
            self.pop(3)
        else:
            #simple var
            self.ST.add_variable(self.stack[-1], self.stack[-2], attributes=None)
            self.pop(2)

    def func_start(self, lookahead):
        # todo: if func==main?!
        self.ST.add_function(self.stack[-1], self.stack[-2], attributes=None)
        func_name = self.stack[-1]
        self.pop(2)
        if func_name != 'main':
            self.push(self.i)
            self.insert_code('')

    def param_end(self, lookahead):
        attr = {'kind': 'param'}
        self.ST.add_variable(self.stack[-1], self.stack[-2], attributes=attr)
        func_name = self.stack[-1]
        self.pop(2)
        self.curr_param_count += 1
        if func_name != 'main':
            self.insert_code(f'(JMP, {self.i}, , )', self.stack[-1])
            self.pop()

    def params_end(self, lookahead):
        attr = {'code_addr': self.i, 'param_count': self.curr_param_count}
        func_stat = self.ST.get_by_name(self.curr_funcs_name[-1])
        func_stat['attr'] = attr
        self.curr_param_count = 0


    def func_end(self, lookahead):
        # todo: if func==main?!
        return_addr = self.ST.get_by_name(self.curr_funcs_name[-1])['attr']['return_addr']
        self.insert_code(f'(JP, @{return_addr}, , )')
        self.curr_funcs_name.pop()


    def set_return_value(self, lookahead):
        addr = self.ST.get_by_name(self.curr_funcs_name[-1])['addr']
        self.insert_code(f'(ASSIGN, {self.stack[-1]}, {addr}, )')
        self.pop()
    

    def func_return(self, lookahead):
        return_addr = self.ST.get_by_name(self.curr_funcs_name[-1])['attr']['return_addr']
        self.insert_code(f'(JP, @{return_addr}, , )')


    def func_arg(self, lookahead):
        i = self.ST.get_index(self.curr_funcs_name[-1])
        self.curr_param_count += 1
        addr = self.ST[i+self.curr_param_count]['addr']
        self.insert_code(f'(ASSIGN, {self.stack[-1]}, {addr}, )')
        self.pop()
    

    def func_call(self, lookahead):
        func = self.ST.get_by_name(self.curr_funcs_name[-1])
        func_addr = func['attr']['code_addr']
        return_addr = func['attr']['return_addr']
        self.insert_code(f'(ASSIGN, #{self.i+2}, {return_addr})')
        self.insert_code(f'(JP, {func_addr}, , )')
        self.curr_param_count = 0

        if func['type'] != 'void':
            # todo: where will we use t??
            t = self.memory.get_tmp()
            self.insert_code(f"(ASSIGN, {func['addr']}, {t}, )")
            self.stack.push(t)
        self.curr_funcs_name.pop()


    def func_name(self, lookahead):
        func = self.ST.get_by_addr(self.stack[-1])
        self.curr_funcs_name.append(func['lexptr'])
        self.pop()




    def code_gen(self, action, lookahead=None):
        semantic_func = getattr(self, action)
        if semantic_func is None:
            print(f'invalid action: {action}')
            return False
        
        semantic_func(lookahead)
        return True
        if (action == 'push'):
            self.push(lookahead)
        elif (action == 'pop'):
            self.pop()
        elif (action == 'save'):
            self.save()
        elif (action == 'jpf_save'):
            self.jpf_save()
        elif (action == 'jp'):
            self.jp()
        elif (action == 'jpf'):
            self.jpf()
        elif (action == 'add_sub'):
            self.add_sub()
        elif (action == 'mult'):
            self.mult()
        elif (action == 'pid'):
            self.pid()
        elif (action == 'assign'):
            self.assign()
        elif (action == 'for_loop'):
            self.for_loop()
        elif (action == 'break_loop'):
            self.break_loop()
