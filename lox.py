# lox.py
#
# Main program

import loxscan

def main(argv):
    if len(argv) != 2:
        raise SystemExit(f'Usage: lox.py filename')
    with open(argv[1]) as file:
        source = file.read()
        
    lexer = loxscan.LoxLexer()
    for tok in lexer.tokenize(source):
        print(tok)

if __name__ == '__main__':
    import sys
    main(sys.argv)
    
    
