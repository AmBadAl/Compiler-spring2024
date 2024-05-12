from scanner import Scanner
from cparser import Parser

if __name__ == '__main__':
    addr = './input.txt'
    scanner = Scanner(addr)
    parser = Parser(scanner)

    parser.parse()
    parser.save_parse_tree('./parse_tree.txt')
    parser.save_syntax_errors('./syntax_errors.txt')
