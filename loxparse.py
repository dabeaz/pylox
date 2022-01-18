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

    @_('{ statement }')
    def statements(self, p):
        return Statements(p.statement)
    
    @_('expression SEMI')
    def statement(self, p):
        return ExpressionStmt(p.expression)
    
    @_('PRINT expression SEMI')
    def statement(self, p):
        return Print(p.expression)

    @_('VAR IDENTIFIER [ EQUAL expression ] SEMI')
    def statement(self, p):
        return VarDeclaration(p.IDENTIFIER, p.expression)

    @_('IDENTIFIER EQUAL expression SEMI')
    def statement(self, p):
        return Assign(p.IDENTIFIER, p.expression)
    
    @_('IF expression LEFT_BRACE statements RIGHT_BRACE [ ELSE LEFT_BRACE statements RIGHT_BRACE ]')
    def statement(self, p):
        return IfStmt(p.expression, p.statements0, p.statements1)
    
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

    @_('IDENTIFIER')
    def expression(self, p):
        return Variable(p.IDENTIFIER)

def test_parsing():
    lexer = LoxLexer()
    parser = LoxParser()

    # Test expression parsing and precedence
    assert parser.parse(lexer.tokenize("print 2;")) == Statements([Print(Literal(2))])
    assert parser.parse(lexer.tokenize('print "hello";')) == Statements([Print(Literal('hello'))])
    assert parser.parse(lexer.tokenize('print true;')) == Statements([Print(Literal(True))])
    assert parser.parse(lexer.tokenize('print false;')) == Statements([Print(Literal(False))])
    assert parser.parse(lexer.tokenize('print nil;')) == Statements([Print(Literal(None))])
    assert parser.parse(lexer.tokenize("print -2+3;")) == Statements([Print(Binary(Unary("-",Literal(2)),"+",Literal(3)))])
    assert parser.parse(lexer.tokenize("print 2+3*4;")) == Statements([Print(Binary(Literal(2), "+",
                                                                        Binary(Literal(3), "*", Literal(4))))])
    assert parser.parse(lexer.tokenize("print 2*3+4;")) == Statements([Print(Binary(Binary(Literal(2), "*", Literal(3)),
                                                                        "+", Literal(4)))])
    assert parser.parse(lexer.tokenize("print 2+3 < 4+5;")) == Statements([Print(
        Binary(Binary(Literal(2), "+", Literal(3)), "<", Binary(Literal(4), "+", Literal(5))))])

    assert parser.parse(lexer.tokenize("print 2 < 3 == 4 < 5;")) == Statements([Print(
        Binary(Binary(Literal(2), "<", Literal(3)), "==", Binary(Literal(4), "<", Literal(5))))])
    
    assert parser.parse(lexer.tokenize("print (2+3)*4;")) == Statements([Print(
        Binary(Grouping(Binary(Literal(2), "+", Literal(3))), "*", Literal(4)))])

if __name__ == '__main__':
    test_parsing()
    
    

