OUTPUT_RETURN_ADDR = 50
OUTPUT_CODE_ADDR = 1


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
        self._initialize()
    
    def _initialize(self):
        self.add_function('output', 'void', None)
        self.table[0]['attr']['code_addr'] = OUTPUT_CODE_ADDR
        self.table[0]['attr']['return_addr'] = OUTPUT_RETURN_ADDR
        self.table[0]['attr']['param_count'] = 1
        self.table[0]['attr']['scope'] = 0
        self.add_variable('a', 'int', {'kind': 'param', 'scope': 1})

    def add_variable(self, lexptr, type, attributes):
        addr = self.mm.get_addr()
        if attributes is None:
            attributes = dict()
        self.table.append({
            'lexptr': lexptr,
            'addr': addr,
            'type': type,
            'attr': attributes
        })
        if 'count' in attributes.keys():
            count = int(attributes['count'][1:]) + 1
        else:
            count = 1
        self.mm.increase(count)

    def add_function(self, lexptr, type, attributes):
        addr = self.mm.get_addr()
        if attributes is None:
            attributes = dict()
        attributes['return_addr'] = self.mm.get_tmp()
        self.table.append({
            'lexptr': lexptr,
            'addr': addr,
            'type': type,
            'attr': attributes
        })
        self.mm.increase(1)

    def get_by_addr(self, addr):
        for row in self.table[::-1]:
            if row['addr'] == addr:
                return row
        return None

    def get_by_name(self, name, scope):
        for row in self.table[::-1]:
            if row['attr']['scope'] > scope:
                continue
            if row['lexptr'] == name:
                return row
        return None

    def get_index(self, name, scope):
        for i, row in zip(range(len(self.table) - 1, -1, -1), self.table[::-1]):
            if row['attr']['scope'] >= scope:
                continue
            if row['lexptr'] == name:
                return i
        return None
    
    def get_type(self, addr, scope):
        if type(addr) == str and addr.startswith('#'):
            return 'int'
        row = self.get_by_addr(addr)
        if row is None:
            return 'int'
        if 'count' in row['attr'].keys():
            return 'array'
        return row['type']
        


class SemanticChecker:

    def __init__(self):
        self.errors = []

    def scoping(self, lineno, id):
        self.errors.append(f"#{lineno} : Semantic Error! '{id}' is not defined.")

    def void_type(self, lineno, id):
        self.errors.append(f"#{lineno} : Semantic Error! Illegal type of void for '{id}'.")
    
    def param_num_matching(self, lineno, id):
        self.errors.append(f"#{lineno} : Semantic Error! Mismatch in numbers of arguments of '{id}'.")
    
    def param_type_matching(self, lineno, N, id, type1, type2):
        self.errors.append(f"#{lineno} : Semantic Error! Mismatch in type of argument {N} of '{id}'. Expected '{type1}' but got '{type2}' instead.")

    def type_mismatch(self, lineno, type1, type2):
        self.errors.append(f"#{lineno} : Semantic Error! Type mismatch in operands, Got {type2} instead of {type1}.")
    
    def break_statement(self, lineno):
        self.errors.append(f"#{lineno} : Semantic Error! No \'for\' found for \'break\'.")
    


class CodeGenerator:

    def __init__(self):
        self.memory = Memory()
        self.ST = SymbolTable(self.memory)
        self.semantic_checker = SemanticChecker()
        self.stack = []
        self.PB = []
        self.i = 0
        self.scope = 0
        self.curr_param_count = 0
        self.curr_funcs_name = []
        self.curr_loops_name = []
        self._initialize()

    def _initialize(self):
        self.insert_code('(JP, 3, , )')
        self.insert_code('(PRINT, 104, , )')
        self.insert_code(f'(JP, @{OUTPUT_RETURN_ADDR}, , )')

    def insert_code(self, code, i=None):
        if (i is None):
            self.PB.append(code)
            self.i += 1
        else:
            self.PB[i] = code

    def push(self, value, lineno=0):
        if type(value) == int:
            self.stack.append(value)
        elif value.isnumeric():
            self.stack.append(f'#{value}')
        else:
            self.stack.append(value)

    def pop(self, n=1, lineno=0):
        if not str(n).isnumeric():
            n = 1
        for i in range(n):
            self.stack.pop()

    def save(self, lookahead, lineno):
        self.push(self.i)
        self.insert_code('')

    def jpf_save(self, lookahead, lineno):
        self.insert_code(f'(JPF, {self.stack[-2]}, {self.i + 1}, )', i=self.stack[-1])
        self.pop(2)
        self.push(self.i)
        self.insert_code('')

    def jp(self, lookahead, lineno):
        self.insert_code(f'(JP, {self.i}, , )', i=self.stack[-1])
        self.pop(1)

    def jpf(self, lookahead, lineno):
        self.insert_code(f'(JPF, {self.stack[-2]}, {self.i}, )', i=self.stack[-1])
        self.pop(2)

    def pid(self, lookahead, lineno):
        row = self.ST.get_by_name(lookahead, self.scope)
        if row is None:
            self.semantic_checker.scoping(lineno, lookahead)
            self.push(self.memory.get_tmp())
        else:
            self.push(row['addr'])
        
    def relop(self, lookahead, lineno):
        a, relop, b = self.stack[-3:]
        type_a, type_b = self.ST.get_type(a, self.scope), self.ST.get_type(b, self.scope)
        if (type_a != type_b):
            self.semantic_checker.type_mismatch(lineno, type_b, type_a)
        t = self.memory.get_tmp()
        if (relop == '=='):
            self.insert_code(f'(EQ, {a}, {b}, {t})')
        else:
            self.insert_code(f'(LT, {a}, {b}, {t})')
        self.pop(3)
        self.push(t)

    def add_sub(self, lookahead, lineno):
        a, op, b = self.stack[-3:]
        type_a, type_b = self.ST.get_type(a, self.scope), self.ST.get_type(b, self.scope)
        if (type_a != type_b):
            self.semantic_checker.type_mismatch(lineno, type_b, type_a)
        t = self.memory.get_tmp()
        if (op == '+'):
            self.insert_code(f'(ADD, {a}, {b}, {t})')
        else:
            self.insert_code(f'(SUB, {a}, {b}, {t})')
        self.pop(3)
        self.push(t)

    def mult(self, lookahead, lineno):
        a, b = self.stack[-2:]
        type_a, type_b = self.ST.get_type(a, self.scope), self.ST.get_type(b, self.scope)
        if (type_a != type_b):
            self.semantic_checker.type_mismatch(lineno, type_b, type_a)
        t = self.memory.get_tmp()
        self.insert_code(f'(MULT, {a}, {b}, {t})')
        self.pop(2)
        self.push(t)

    def assign(self, lookahead, lineno):
        b, a = self.stack[-2:]
        type_b, type_a = self.ST.get_type(b, self.scope), self.ST.get_type(a, self.scope)
        if (type_a != type_b):
            self.semantic_checker.type_mismatch(lineno, type_a, type_b)
        self.insert_code(f'(ASSIGN, {a}, {b})')
        self.pop(1)
    
    def get_arr(self, lookahead, lineno):
        t1 = self.memory.get_tmp()
        self.insert_code(f'(MULT, #4, {self.stack[-1]}, {t1})')
        self.pop()
        t2 = self.memory.get_tmp()
        self.insert_code(f'(ADD, {self.stack[-1]}, {t1}, {t2})')
        self.pop()
        self.push(f'@{t2}')

    def for_loop(self, lookahead, lineno):
        t = self.memory.get_tmp()
        self.curr_loops_name.append(t)
        self.push(t)
        self.push(self.i)
        self.insert_code('')

    def for_label(self, lookahead, lineno):
        self.push(self.i)
    
    def for_jpf(self, lookahead, lineno):
        self.push(self.i)
        self.insert_code('')
        self.push(self.i)
        self.insert_code('')
    
    def for_jp_loop(self, lookahead, lineno):
        for_label = self.stack[-4]
        self.insert_code(f'(JP, {for_label}, , )')

    def for_statement(self, lookahead, lineno):
        self.scope += 1
        for_jpf = self.stack[-1]
        self.insert_code(f'(JP, {self.i}, , )', i=for_jpf)

    def for_jp(self, lookahead, lineno):
        t, for_begin, for_label, rel_op, for_jpf, for_step = self.stack[-6:]
        self.insert_code(f'(JP, {for_step+1}, , )')
        self.insert_code(f'(ASSIGN, #{self.i}, {t}, )', i=for_begin)
        self.insert_code(f'(JPF, {rel_op}, {self.i}, )', i=for_jpf)
        self.pop(6)
        self.curr_loops_name.pop()
        self.scope -= 1

    def break_loop(self, lookahead, lineno):
        # check semantic error: break
        if len(self.curr_loops_name) == 0:
            self.semantic_checker.break_statement(lineno)
            self.curr_loops_name.append(self.memory.get_tmp())

        t = self.curr_loops_name[-1]
        self.insert_code(f'(JP, @{t}, , )')
    
    def var_end(self, lookahead, lineno):
        if self.stack[-1].startswith('#'):
            #array
            arr_type = self.stack[-3]
            if arr_type == 'void':
                self.semantic_checker.void_type(lineno=lineno, id=self.stack[-2])
            else:
                attr = {'count': self.stack[-1], 'scope': self.scope}
                self.ST.add_variable(self.stack[-2], self.stack[-3], attributes=attr)
                arr = self.ST.table[-1]['addr']
                first_elem_addr = arr + 4
                self.insert_code(f"(ASSIGN, #{first_elem_addr}, {arr}, )")
            self.pop(3)
        else:
            #simple var
            var_type = self.stack[-2]
            if var_type == 'void':
                self.semantic_checker.void_type(lineno=lineno, id=self.stack[-1])
            else:
                attr = {'scope': self.scope}
                self.ST.add_variable(self.stack[-1], self.stack[-2], attributes=attr)
            self.pop(2)

    def func_start(self, lookahead, lineno):
        attr = {'scope': self.scope}
        self.ST.add_function(self.stack[-1], self.stack[-2], attributes=attr)
        self.scope += 1
        func_name = self.stack[-1]
        self.curr_funcs_name.append(func_name)
        self.pop(2)
        if func_name != 'main':
            self.push(self.i)
            self.insert_code('')

    def param_end(self, lookahead, lineno):
        param_type = self.stack[-2]
        if param_type == 'void':
            self.semantic_checker.void_type(lineno=lineno, id=self.stack[-1])
        else:
            attr = {'kind': 'param', 'scope': self.scope}
            self.ST.add_variable(self.stack[-1], self.stack[-2], attributes=attr)
            self.curr_param_count += 1
        self.pop(2)

    def param_arr_end(self, lookahead, lineno):
        param_type = self.stack[-2]
        if param_type == 'void':
            self.semantic_checker.void_type(lineno=lineno, id=self.stack[-1])
        else:
            attr = {'kind': 'param', 'scope': self.scope, 'count': '#10'}
            self.ST.add_variable(self.stack[-1], self.stack[-2], attributes=attr)
            self.curr_param_count += 1
        self.pop(2)

    def params_end(self, lookahead, lineno):
        print(self.curr_funcs_name[-1])
        func_stat = self.ST.get_by_name(self.curr_funcs_name[-1], self.scope)
        func_stat['attr']['code_addr'] = self.i
        func_stat['attr']['param_count'] = self.curr_param_count
        self.curr_param_count = 0


    def func_end(self, lookahead, lineno):
        return_addr = self.ST.get_by_name(self.curr_funcs_name[-1], self.scope)['attr']['return_addr']
        self.scope -= 1
        func_name = self.curr_funcs_name[-1]
        if func_name != 'main':
            self.insert_code(f'(JP, @{return_addr}, , )')
            self.insert_code(f'(JP, {self.i}, , )', self.stack[-1])
            self.pop()
        self.curr_funcs_name.pop()


    def set_return_value(self, lookahead, lineno):
        addr = self.ST.get_by_name(self.curr_funcs_name[-1], self.scope)['addr']
        self.insert_code(f'(ASSIGN, {self.stack[-1]}, {addr}, )')
        self.pop()
    

    def func_return(self, lookahead, lineno):
        return_addr = self.ST.get_by_name(self.curr_funcs_name[-1], self.scope)['attr']['return_addr']
        self.insert_code(f'(JP, @{return_addr}, , )')


    def func_arg(self, lookahead, lineno):
        i = self.ST.get_index(self.curr_funcs_name[-1], self.scope)
        self.curr_param_count += 1
        func_arg = self.ST.table[i+self.curr_param_count]

        # check semantic error: num of arguments
        func = self.ST.get_by_name(self.curr_funcs_name[-1], self.scope)
        if self.curr_param_count > func['attr']['param_count']:
            self.semantic_checker.param_num_matching(lineno, func['lexptr'])
        # check semantic error: argument type
        else:
            func_arg_type = self.ST.get_type(func_arg['addr'], self.scope)
            invoke_arg_type = self.ST.get_type(self.stack[-1], self.scope)
            if func_arg_type != invoke_arg_type:
                self.semantic_checker.param_type_matching(
                    lineno, self.curr_param_count, self.curr_funcs_name[-1],func_arg_type, invoke_arg_type)

        addr = func_arg['addr']
        self.insert_code(f'(ASSIGN, {self.stack[-1]}, {addr}, )')
        self.pop()
    

    def func_call(self, lookahead, lineno):
        func = self.ST.get_by_name(self.curr_funcs_name[-1], self.scope)
        func_addr = func['attr']['code_addr']
        return_addr = func['attr']['return_addr']
        self.insert_code(f'(ASSIGN, #{self.i+2}, {return_addr})')
        self.insert_code(f'(JP, {func_addr}, , )')
        self.curr_param_count = 0

        t = self.memory.get_tmp()
        if func['type'] != 'void':
            self.insert_code(f"(ASSIGN, {func['addr']}, {t}, )")
        self.push(t)
        self.curr_funcs_name.pop()


    def func_name(self, lookahead, lineno):
        print(self.stack[-1])
        func = self.ST.get_by_addr(self.stack[-1])
        self.curr_funcs_name.append(func['lexptr'])
        self.pop()


    def signed_fac(self, lookahead, lineno):
        sign, factor = self.stack[-2:]
        self.pop(2)
        if sign == '-' and str(factor).startswith('#'):
            t = self.memory.get_tmp()
            self.insert_code(f'(SUB, #0, {factor}, {t})')
            factor = t
        elif sign == '-':
            self.insert_code(f'(SUB, #0, {factor}, {factor})')
        self.push(factor)
        

    def code_gen(self, action, lineno, lookahead=None):
        semantic_func = getattr(self, action)
        if semantic_func is None:
            print(f'invalid action: {action}')
            return False
        
        semantic_func(lookahead, lineno)
        return True
