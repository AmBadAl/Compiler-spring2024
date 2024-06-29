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
