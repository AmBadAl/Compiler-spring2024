from cparser import Parser

FOLLOWS_LIST = './grammar_info/follows_list.txt'
PREDICTS_LIST = './grammar_info/predicts_list.txt'
GRAMMAR = './grammar_info/grammar_new.txt'


if __name__ == '__main__':
    addr = './input.txt'
    parser = Parser(addr, FOLLOWS_LIST, PREDICTS_LIST, GRAMMAR)

    parser.parse()
    parser.save_parse_tree('./parse_tree.txt')
    parser.save_syntax_errors('./syntax_errors.txt')
