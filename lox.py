# lox.py
#
# Main program

import sys

import loxscan
import loxparse
import loxast
import loxinterp

def main(argv):
    if len(argv) > 2:
        raise SystemExit(f'Usage: lox.py filename')
    if len(sys.argv) == 2:
        with open(argv[1]) as file:
            source = file.read()
    else:
        source = input("Lox > ")
        
    lexer = loxscan.LoxLexer()
    parser = loxparse.LoxParser()
    ast = parser.parse(lexer.tokenize(source))
    print(loxast.ASTPrinter().visit(ast))

    print("::: Running :::")
    interp = loxinterp.LoxInterpreter()
    interp.visit(ast)
    

if __name__ == '__main__':
    import sys
    main(sys.argv)
    
    
