# loxparse.py

from sly import Parser
from loxast import *
from loxscan import LoxLexer

class LoxParser(Parser):
    tokens = LoxLexer.tokens

    precedence = (
        ('right', EQUAL),
        ('left', OR),
        ('left', AND),
        ('left', EQUAL_EQUAL, BANG_EQUAL),
        ('left', LESS, LESS_EQUAL, GREATER, GREATER_EQUAL),
        ('left', PLUS, MINUS),
        ('left', STAR, SLASH),
        ('right', UNARY),
        )

    @_('declarations')
    def program(self, p):
        return p.declarations


    @_('{ declaration }')
    def declarations(self, p):
        return Statements(p.declaration)

    @_('var_declaration')
    def declaration(self, p):
        return p.var_declaration
    
    @_('VAR IDENTIFIER [ EQUAL expression ] SEMI')
    def var_declaration(self, p):
        return VarDeclaration(p.IDENTIFIER, p.expression)
    
    @_('statement')
    def declaration(self, p):
        return p.statement

    @_('statement_block',
       'expression_statement',
       'print_statement',
       'if_statement',
       'while_statement',
       'for_statement')
    def statement(self, p):
        return p[0]
    
    @_('LEFT_BRACE declarations RIGHT_BRACE')
    def statement_block(self, p):
        return p.declarations

    @_('expression SEMI')
    def expression_statement(self, p):
        return ExpressionStmt(p.expression)
    
    @_('PRINT expression SEMI')
    def print_statement(self, p):
        return Print(p.expression)


    @_('IF LEFT_PAREN expression RIGHT_PAREN statement [ ELSE statement ]')
    def if_statement(self, p):
        return IfStmt(p.expression, p.statement0, p.statement1)

    @_('WHILE LEFT_PAREN expression RIGHT_PAREN statement')
    def while_statement(self, p):
        return WhileStmt(p.expression, p.statement)

    @_('FOR LEFT_PAREN for_initializer [ expression ] SEMI [ expression ] RIGHT_PAREN statement')
    def for_statement(self, p):
        body = p.statement
        if p.expression1:
            body.statements.append(p.expression1)
        body = WhileStmt(p.expression0, body)
        body = Statements([p.for_initializer, body])
        return body

    @_('FOR LEFT_PAREN SEMI [ expression ] SEMI [ expression ] RIGHT_PAREN statement')
    def for_statement(self, p):
        body = p.statement
        if p.expression1:
            body.statements.append(p.expression1)
        body = WhileStmt(p.expression0, body)
        return body
    
    @_('var_declaration',
       'expression_statement')
    def for_initializer(self, p):
        return p[0]

    @_('IDENTIFIER EQUAL expression')
    def expression(self, p):
        return Assign(p.IDENTIFIER, p.expression)
                
    @_('expression OR expression',
       'expression AND expression',
    )
    def expression(self, p):
        return Logical(p.expression0, p[1], p.expression1)
    
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
    
    

