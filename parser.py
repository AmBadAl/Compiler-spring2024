FOLLOWS_LIST = './follows_list.txt'
PREDICTS_LIST = './predicts_list.txt'


class Parser():
    def __init__(self, scanner):
        self.follows_list = self._read_follows(FOLLOWS_LIST)
        self.predict_list = self._read_predicts(PREDICTS_LIST)
        self.scanner = scanner
        self.look_ahead = None

    def _read_follows(self, addr):
        result = dict()
        with open(addr, 'r') as f:
            all_lines = f.readlines()
            for line in all_lines:
                infos = line[:-1].split('\t')
                result[infos[0]] = infos[1:]
        return result

    def _read_predicts(self, addr):
        result = dict()
        with open(addr, 'r') as f:
            all_lines = f.readlines()
            for line in all_lines:
                infos = line[:-1].split('\t')
                result[int(infos[0])] = infos[1:]
        return result

    def parse(self):
        pass

    def _Match(self, expected):
        if self.look_ahead == expected:
            return True
        else:
            return False

    def _Program(self):
        if self.look_ahead in self.predict_list[1]:
            return self._Declaration_list()
        elif self.look_ahead in self.follows_list['Program']:
            print('error missing')
            return False
        else:
            print(f'illigal {self.look_ahead}')
            # get_next_token
            return self._Program()
        
    def _Declaration_list(self):
        if self.look_ahead in self.predict_list[2]:
            return self._Declaration() and self._Declaration_list()
        elif self.look_ahead in self.predict_list[3]:
            return True
        elif self.look_ahead in self.follows_list['Declaration_list']:
            print('error missing')
            return False
        else:
            print(f'illigal {self.look_ahead}')
            # get_next_token
            return self._Declaration_list()
        
    def _Declaration(self):
        if self.look_ahead in self.predict_list[4]:
            return self._Declaration_initial() and self.Declaration_prime()
        elif self.look_ahead in self.follows_list['Declaration']:
            print('error missing')
            return False
        else:
            print(f'illigal {self.look_ahead}')
            # get_next_token
            return self._Declaration()
    

    def _Declaration_initial(self):
        if self.look_ahead in self.predict_list[5]:
            return self._Type_specifier() and self._Match("ID")
        elif self.look_ahead in self.follows_list['Declaration_initial']:
            print('error missing')
            return False
        else:
            print(f'illigal {self.look_ahead}')
            # get_next_token
            return self._Declaration_initial()

    def _Declaration_prime(self):
        pass
    def _Var_declaration_prime(self):
        pass
    def _Fun_declaration_prime(self):
        pass
    def _Type_specifier(self):
        pass
    def _Params(self):
        pass
    def _Param_list(self):
        pass
    def _Param(self):
        pass
    def _Param_prime(self):
        pass
    def _Compound_stmt(self):
        pass
    def _Statement_list(self):
        pass
    def _Statement(self):
        pass
    def _Expression_stmt(self):
        pass
    def _Selection_stmt(self):
        pass
    def _Else_stmt(self):
        pass
    def _Iteration_stmt(self):
        pass
    def _Return_stmt(self):
        pass
    def _Return_stmt_prime(self):
        pass
    def _Expression(self):
        pass
    def _B(self):
        pass
    def _H(self):
        pass

if __name__ == '__main__':
    parser = Parser(None)
