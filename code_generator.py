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
    
    def add_variable(self, lexptr, type, attributes):
        addr = self.mm.get_addr()
        self.table.append({
            'lexptr': lexptr,
            'addr': addr,
            'type': type,
            'attributes': attributes
        })
        count = attributes['count']
        self.mm.increase(count)

    def add_function(self, lexptr, type, attributes):
        addr = self.mm.get_addr()
        attributes['return_addr'] = self.mm.get_tmp()
        self.table.append({
            'lexptr': lexptr,
            'addr': addr,
            'type': type,
            'attributes': attributes
        })
        self.mm.increase(1)


class CodeGenerator:

    def __init__(self):
        self.memory = Memory()
        self.ST = SymbolTable(self.memory)
        self.stack = []
        self.PB = []
        self.i = 0


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

    def save(self):
        self.push(self.i)
        self.i += 1

    def jpf_save(self):
        self.insert_code(f'(JPF, {self.stack[-2]}, {self.i + 1}, )', i=self.stack[-1])
        self.pop(2)
        self.push(self.i)
        # self.insert_code("(, , , )")

    def jp(self):
        self.insert_code(f'(JPF, {self.i}, , )', i=self.stack[-1])
        self.pop(1)

    def jpf(self):
        self.insert_code(f'(JPF, {self.stack[-2]}, {self.i}, )', i=self.stack[-1])
        self.pop(2)

    def pid(self):
        #todo
        return
        

    def add_sub(self):
        a, op, b = self.stack[-3:]
        #todo: check type of a and b for semantic errors
        t = self.memory.get_tmp()
        if (op == '+'):
            self.insert_code(f'(ADD, {a}, {b}, {t})')
        else:
            self.insert_code(f'(SUB, {a}, {b}, {t})')
        self.pop(3)
        self.push(t)

    def mult(self):
        a, b = self.stack[-2:]
        #todo: check type of a and b for semantic errors
        t = self.memory.get_tmp()
        self.insert_code(f'(MULT, {a}, {b}, {t})')
        self.pop(2)
        self.push(t)

    def assign(self):
        b, a = self.stack[-2:]
        #todo: check type of a and b for semantic errors
        self.insert_code(f'(ASSIGN, {a}, {b})')
        self.pop(1)

    def for_loop(self):
        #todo
        return

    def break_loop(self):
        #todo
        return
    

    def code_gen(self, action, lookahead):
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
