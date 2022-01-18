# lox.py
#
# Main program

import loxscan
import loxparse
import loxast

def main(argv):
    if len(argv) != 2:
        raise SystemExit(f'Usage: lox.py filename')
    with open(argv[1]) as file:
        source = file.read()
        
    lexer = loxscan.LoxLexer()
    parser = loxparse.LoxParser()
    ast = parser.parse(lexer.tokenize(source))
    print(loxast.ASTPrinter().visit(ast))

if __name__ == '__main__':
    import sys
    main(sys.argv)
    
    
