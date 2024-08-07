from anytree import Node, RenderTree
from scanner import Scanner
from code_generator import CodeGenerator

class Parser():
    def __init__(self, input_addr, follows_path, predicts_path, grammar_path):
        self.scanner = self._get_scanner(input_addr)
        self.follows_list = self._read_follows(follows_path)
        self.predict_list = self._read_predicts(predicts_path)
        self.productions = self._read_productions(grammar_path)
        self._generate_functions()
        self.look_ahead = None
        self.token = None
        self.line_number = None
        self.syntax_errors = []
        self.root = Node('Program')
        self.current_node = self.root

        self.code_generator = CodeGenerator()

    def _get_scanner(self, input_addr):
        return Scanner(input_addr)

    def _read_follows(self, addr):
        follows = dict()
        with open(addr, 'r') as f:
            all_lines = f.readlines()
            for line in all_lines:
                infos = line.strip().split('\t')
                follows[infos[0]] = infos[1:]
        return follows

    def _read_predicts(self, addr):
        predicts = dict()
        with open(addr, 'r') as f:
            all_lines = f.readlines()
            for line in all_lines:
                infos = line.strip().split('\t')
                predicts[int(infos[0])] = infos[1:]
        return predicts

    def _read_productions(self, addr):
        productions = dict()
        with open(addr, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                infos = line.strip().split('->')
                NT = infos[0]
                RHS = infos[1].strip().split(' ')

                if NT not in productions.keys():
                    productions[NT] = [(i+1, RHS)]
                else:
                    productions[NT] += [(i+1, RHS)]
        return productions

    def _generate_functions(self):
        self.PRD_functions = dict()
        NT_list = self.productions.keys()

        for NT in NT_list:
            self.PRD_functions[NT] = None

        for NT in NT_list:
            def NT_function(NT=NT):
                if self.look_ahead == '':
                    self.current_node.parent = None
                    return False
                # check productions predict set
                for prod in self.productions[NT]:
                    prod_num, prod_elem = prod
                    if self.look_ahead in self.predict_list[prod_num]:
                        result = True
                        for elem in prod_elem:
                            if elem == '':
                                Node('epsilon', parent=self.current_node)
                                continue
                            elif elem in NT_list:
                                new_node = Node(elem.replace('_', '-'), parent=self.current_node)
                                old_node = self.current_node
                                self.current_node = new_node
                                result = result and self.PRD_functions[elem]()
                                self.current_node = old_node
                            elif elem.startswith("#"):
                                token_lex = self.token[1]
                                result = result and self.code_generator.code_gen(elem[1:], lineno=self.line_number, lookahead=token_lex)
                            else:
                                new_node = Node(self.token, parent=self.current_node)
                                old_node = self.current_node
                                self.current_node = new_node
                                result = result and self._Match(elem)
                                self.current_node = old_node
                            
                            if not result:
                                return result
                        print(prod_num)
                        return result

                # check NT follow set for synchronization
                if self.look_ahead in self.follows_list[NT]:
                    print(f'missing {NT}')
                    name = NT.replace('_', '-')
                    self.syntax_errors.append((self.line_number, f"missing {name}"))
                    self.current_node.parent = None
                    return True
                else:
                    if self.look_ahead == '$':
                        self.syntax_errors.append((self.line_number, f'Unexpected EOF'))
                        print(f'Unexpected EOF')
                    else:
                        self.syntax_errors.append((self.line_number, f'illegal {self.look_ahead}'))
                        print(f'illegal {self.look_ahead}')
                    
                    self.look_ahead = self._get_next_token()
                    return self.PRD_functions[NT]()

            self.PRD_functions[NT] = NT_function

    def _Match(self, expected):
        if self.look_ahead == '':
            return False
        elif self.look_ahead == expected:
            self.look_ahead = self._get_next_token()
            return True
        else:
            print(f'missing {expected}')
            self.current_node.parent = None
            self.syntax_errors.append(
                (self.line_number, f'missing {expected}'))
            return True

    def _get_next_token(self):
        while True:
            token, line_number = self.scanner.get_next_token()
            if token[0] in ['NUM', 'ID']:
                self.token = token
                self.line_number = line_number
                return token[0]
            elif token[0] in ['KEYWORD', 'SYMBOL', 'EOF']:
                self.token = token
                self.line_number = line_number
                if self.look_ahead == '$':
                    return ''
                return token[1]

    def parse(self):
        self.look_ahead = self._get_next_token()
        parse_result = self.PRD_functions['Program']()
        if parse_result:
            Node('$', parent=self.root)
        return parse_result 
    
    def save_parse_tree(self, addr):
        with open(addr, 'w', encoding="utf-8") as f:
            for pre, _, node in RenderTree(self.root):
                f.write(f'{pre}{node.name}\n'.replace("'", ''))
    
    def save_syntax_errors(self, addr):
        with open(addr, 'w', encoding='utf-8') as f:
            if len(self.syntax_errors) == 0:
                f.write('There is no syntax error.')
            else:
                for error in self.syntax_errors:
                    f.write(f'#{error[0]} : syntax error, {error[1]}\n')

    def save_output(self, addr):
        with open(addr, 'w', encoding='utf-8') as f:
            if (len(self.code_generator.semantic_checker.errors) == 0):
                for line, code in enumerate(self.code_generator.PB):
                    f.write(f'{line}\t{code}\n')
            else:
                self._save_semantic_errors()
                f.write("The output code has not been generated.")
    
    def _save_semantic_errors(self):
        with open('./semantic_errors.txt', 'w', encoding='utf-8') as f:
            for line, code in enumerate(self.code_generator.semantic_checker.errors):
                f.write(f'{code}\n')



if __name__ == '__main__':
    parser = Parser(None)
