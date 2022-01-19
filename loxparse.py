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

    @_('var_declaration',
       'func_declaration')
    def declaration(self, p):
        return p[0]
    
    @_('VAR IDENTIFIER [ EQUAL expression ] SEMI')
    def var_declaration(self, p):
        return VarDeclaration(p.IDENTIFIER, p.expression)

    @_('FUN IDENTIFIER LEFT_PAREN parameters RIGHT_PAREN statement_block')
    def func_declaration(self, p):
        return FuncDeclaration(p.IDENTIFIER, p.parameters, p.statement_block)

    @_('FUN IDENTIFIER LEFT_PAREN RIGHT_PAREN statement_block')
    def func_declaration(self, p):
        return FuncDeclaration(p.IDENTIFIER, [], p.statement_block)

    @_('IDENTIFIER { COMMA IDENTIFIER }')
    def parameters(self, p):
        return [ p.IDENTIFIER0 ] + p.IDENTIFIER1
    
    @_('statement')
    def declaration(self, p):
        return p.statement

    @_('statement_block',
       'expression_statement',
       'print_statement',
       'if_statement',
       'while_statement',
       'for_statement',
       'return_statement')
    def statement(self, p):
        return p[0]
    
    @_('LEFT_BRACE declarations RIGHT_BRACE')
    def statement_block(self, p):
        return p.declarations

    @_('expression SEMI')
    def expression_statement(self, p):
        return ExprStmt(p.expression)
    
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
            if not isinstance(body, Statements):
                body = Statements([body])
            body.statements.append(ExprStmt(p.expression1))
        body = WhileStmt(p.expression0 or Literal(True), body)
        body = Statements([p.for_initializer, body])
        return body

    @_('FOR LEFT_PAREN SEMI [ expression ] SEMI [ expression ] RIGHT_PAREN statement')
    def for_statement(self, p):
        body = p.statement
        if p.expression1:
            if not isinstance(body, Statements):
                body = Statements([body])
            body.statements.append(ExprStmt(p.expression1))
        body = WhileStmt(p.expression0 or Literal(True), body)
        return body
    
    @_('var_declaration',
       'expression_statement')
    def for_initializer(self, p):
        return p[0]

    @_('RETURN expression SEMI')
    def return_statement(self, p):
        return Return(p.expression)
    
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

    @_('factor')
    def expression(self, p):
        return p.factor
    
    @_('LEFT_PAREN expression RIGHT_PAREN')
    def factor(self, p):
        return Grouping(p.expression)

    @_('MINUS factor %prec UNARY',
       'BANG factor %prec UNARY')
    def factor(self, p):
        return Unary(p[0], p.factor)

    @_('NUMBER',
       'STRING',
       )
    def factor(self, p):
        return Literal(p[0])

    @_('TRUE',
       'FALSE')
    def factor(self, p):
        return Literal(p[0] == 'true')

    @_('NIL')
    def factor(self, p):
        return Literal(None)

    @_('IDENTIFIER')
    def factor(self, p):
        return Variable(p.IDENTIFIER)

    @_('factor LEFT_PAREN arguments RIGHT_PAREN')
    def factor(self, p):
        return Call(p.factor, p.arguments)

    @_('factor LEFT_PAREN RIGHT_PAREN')
    def factor(self, p):
        return Call(p.factor, [])

    @_('expression { COMMA expression }')
    def arguments(self, p):
        return [ p.expression0 ] + p.expression1

def test_parsing():
    lexer = LoxLexer()
    parser = LoxParser()

    def parse(source):
        return parser.parse(lexer.tokenize(source))
    
    # Test expression parsing and precedence
    assert parse("2;") == Statements([ExprStmt(Literal(2))])
    assert parse('"hello";') == Statements([ExprStmt(Literal('hello'))])
    assert parse('true;') == Statements([ExprStmt(Literal(True))])
    assert parse('false;') == Statements([ExprStmt(Literal(False))])
    assert parse('nil;') == Statements([ExprStmt(Literal(None))])
    assert parse("-2+3;") == Statements([ExprStmt(Binary(Unary("-",Literal(2)),"+",Literal(3)))])
    assert parse("2+3*4;") == Statements([ExprStmt(Binary(Literal(2), "+",
                                                                        Binary(Literal(3), "*", Literal(4))))])
    assert parse("2*3+4;") == Statements([ExprStmt(Binary(Binary(Literal(2), "*", Literal(3)),
                                                                        "+", Literal(4)))])
    assert parse("2+3 < 4+5;") == Statements([ExprStmt(
        Binary(Binary(Literal(2), "+", Literal(3)), "<", Binary(Literal(4), "+", Literal(5))))])

    assert parse("2 < 3 == 4 < 5;") == Statements([ExprStmt(
        Binary(Binary(Literal(2), "<", Literal(3)), "==", Binary(Literal(4), "<", Literal(5))))])
    
    assert parse("(2+3)*4;") == Statements([ExprStmt(
        Binary(Grouping(Binary(Literal(2), "+", Literal(3))), "*", Literal(4)))])

    assert parse("x + y(2);") == Statements([ExprStmt(
        Binary(Variable('x'), "+", Call(Variable("y"), [Literal(2)])))])

    assert parse("x = y(2);") == Statements([ExprStmt(
        Assign("x", Call(Variable("y"), [Literal(2)])))])

    # Tests of various statements
    assert parse("print 2;") == Statements([
        Print(Literal(2))])

    assert parse("var x;") == Statements([
        VarDeclaration("x", None)])

    assert parse("var x = 2;") == Statements([
        VarDeclaration("x", Literal(2))])

    assert parse("return 2;") == Statements([
        Return(Literal(2))])

    assert parse("if (x < 1) print x; else print y;") == Statements([
        IfStmt(Binary(Variable('x'), '<', Literal(1)),
               Print(Variable('x')),
               Print(Variable('y')))])

    assert parse("if (x < 1) print x;") == Statements([
        IfStmt(Binary(Variable('x'), '<', Literal(1)),
               Print(Variable('x')),
               None)])

    assert parse("while (x < 10) x = x + 1;") == Statements([
        WhileStmt(Binary(Variable('x'), '<', Literal(10)),
                  ExprStmt(Assign('x', Binary(Variable('x'), '+', Literal(1)))))])

    assert parse("for (var x = 1; x < 10; x = x + 1) print x;") == Statements([
        Statements([
            VarDeclaration("x", Literal(1)),
            WhileStmt(Binary(Variable('x'), '<', Literal(10)), Statements([
                Print(Variable('x')),
                ExprStmt(Assign('x', Binary(Variable('x'), '+', Literal(1))))]))
            ])])

    assert parse("for (;x < 10; x = x + 1) print x;") == Statements([
            WhileStmt(Binary(Variable('x'), '<', Literal(10)), Statements([
                Print(Variable('x')),
                ExprStmt(Assign('x', Binary(Variable('x'), '+', Literal(1))))]))
            ])

    assert parse("for (;x < 10;) print x;") == Statements([
            WhileStmt(Binary(Variable('x'), '<', Literal(10)), 
                      Print(Variable('x')))])

    assert parse("for (;;) print x;") == Statements([
            WhileStmt(Literal(True), 
                Print(Variable('x')))])

    assert parse("fun square(x) { return x*x; }") == Statements([
        FuncDeclaration('square', ['x'], Statements([
            Return(Binary(Variable('x'), '*', Variable('x')))]))])
    
if __name__ == '__main__':
    test_parsing()
    
    

