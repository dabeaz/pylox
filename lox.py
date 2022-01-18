# lox.py
#
# Main program

import loxscan
import loxparse

def main(argv):
    if len(argv) != 2:
        raise SystemExit(f'Usage: lox.py filename')
    with open(argv[1]) as file:
        source = file.read()
        
    lexer = loxscan.LoxLexer()
    parser = loxparse.LoxParser()
    ast = parser.parse(lexer.tokenize(source))
    print(ast)

if __name__ == '__main__':
    import sys
    main(sys.argv)
    
    
