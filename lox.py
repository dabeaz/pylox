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

    lexer = loxscan.LoxLexer()
    parser = loxparse.LoxParser()
    interp = loxinterp.LoxInterpreter()
    
    if len(sys.argv) == 2:
        with open(argv[1]) as file:
            source = file.read()
        ast = parser.parse(lexer.tokenize(source))
        print(loxast.ASTPrinter().visit(ast))
        print("::: Running :::")
        interp.interpret(ast)
    else:
        try:
            while True:
                source = input("Lox > ")
                ast = parser.parse(lexer.tokenize(source))
                # Strip away the outer Statements block so we keep global scope
                for stmt in ast.statements:
                    interp.interpret(stmt)
        except EOFError:
            pass

if __name__ == '__main__':
    import sys
    main(sys.argv)
    
    
