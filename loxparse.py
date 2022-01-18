# loxparse.py

from sly import Parser
from loxast import *
from loxscan import LoxLexer

class LoxParser(Parser):
    tokens = LoxLexer.tokens

    precedence = (
        ('left', EQUAL_EQUAL, BANG_EQUAL),
        ('left', LESS, LESS_EQUAL, GREATER, GREATER_EQUAL),
        ('left', PLUS, MINUS),
        ('left', STAR, SLASH),
        ('right', UNARY),
        )
    
    @_('PRINT expression SEMI')
    def print_statement(self, p):
        return Print(p.expression)
    
    @_('expression PLUS expression',
       'expression MINUS expression',
       'expression STAR expression',
       'expression SLASH expression',
       'expression LESS expression',
       'expression LESS_EQUAL expression',
       'expression GREATER expression',
       'expression GREATER_EQUAL expression',
       'expression EQUAL_EQUAL expression',
       'expression BANG_EQUAL expression',
       )
    def expression(self, p):
        return Binary(p.expression0, p[1], p.expression1)

    @_('LEFT_PAREN expression RIGHT_PAREN')
    def expression(self, p):
        return Grouping(p.expression)

    @_('MINUS expression %prec UNARY',
       'BANG expression %prec UNARY')
    def expression(self, p):
        return Unary(p[0], p.expression)

    @_('NUMBER',
       'STRING',
       )
    def expression(self, p):
        return Literal(p[0])

    @_('TRUE',
       'FALSE')
    def expression(self, p):
        return Literal(p[0] == 'true')

    @_('NIL')
    def expression(self, p):
        return Literal(None)


def test_parsing():
    lexer = LoxLexer()
    parser = LoxParser()

    # Test expression parsing and precedence
    assert parser.parse(lexer.tokenize("print 2;")) == Print(Literal(2))
    assert parser.parse(lexer.tokenize('print "hello";')) == Print(Literal('hello'))
    assert parser.parse(lexer.tokenize('print true;')) == Print(Literal(True))
    assert parser.parse(lexer.tokenize('print false;')) == Print(Literal(False))
    assert parser.parse(lexer.tokenize('print nil;')) == Print(Literal(None))        
    assert parser.parse(lexer.tokenize("print -2+3;")) == Print(Binary(Unary("-",Literal(2)),"+",Literal(3)))
    assert parser.parse(lexer.tokenize("print 2+3*4;")) == Print(Binary(Literal(2), "+",
                                                                        Binary(Literal(3), "*", Literal(4))))
    assert parser.parse(lexer.tokenize("print 2*3+4;")) == Print(Binary(Binary(Literal(2), "*", Literal(3)),
                                                                        "+", Literal(4)))
    assert parser.parse(lexer.tokenize("print 2+3 < 4+5;")) == Print(
        Binary(Binary(Literal(2), "+", Literal(3)), "<", Binary(Literal(4), "+", Literal(5))))

    assert parser.parse(lexer.tokenize("print 2 < 3 == 4 < 5;")) == Print(
        Binary(Binary(Literal(2), "<", Literal(3)), "==", Binary(Literal(4), "<", Literal(5))))        

    assert parser.parse(lexer.tokenize("print (2+3)*4;")) == Print(
        Binary(Grouping(Binary(Literal(2), "+", Literal(3))), "*", Literal(4)))

if __name__ == '__main__':
    test_parsing()
    
    

