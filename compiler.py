from scanner import Scanner
from cparser import Parser

if __name__ == '__main__':
    addr = 'P2_testcases_10(14022)\T01\input.txt'
    scanner = Scanner(addr)
    parser = Parser(scanner)

    parser.parse()
    parser.save_parse_tree('./parse_tree.txt')
