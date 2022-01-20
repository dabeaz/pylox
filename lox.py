# lox.py
#
# Main program

import sys

import loxcontext

def main(argv):
    if len(argv) > 2:
        raise SystemExit(f'Usage: lox.py filename')

    context = loxcontext.LoxContext()
    if len(sys.argv) == 2:
        with open(argv[1]) as file:
            source = file.read()
        context.parse(source)
        context.run()
    else:
        try:
            while True:
                source = input("Lox > ")
                context.parse(source)
                if not context.have_errors:
                    for stmt in context.ast.statements:
                        context.ast = stmt
                        context.run()
        except EOFError:
            pass

if __name__ == '__main__':
    import sys
    main(sys.argv)
    
    
