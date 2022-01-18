# loxscan.py

from sly import Lexer

class LoxLexer(Lexer):
    tokens = { LEFT_PAREN, RIGHT_PAREN, LEFT_BRACE, RIGHT_BRACE,
               COMMA, DOT, MINUS, PLUS, STAR, SLASH, SEMI,
               EQUAL, EQUAL_EQUAL, BANG, BANG_EQUAL, LESS, LESS_EQUAL,
               GREATER, GREATER_EQUAL, 
               NUMBER, IDENTIFIER, STRING,
               AND, CLASS, ELSE, FALSE, FOR, FUN, IF, NIL,
               OR, PRINT, RETURN, SUPER, THIS, TRUE, VAR, WHILE
               }

    ignore = ' \t'

    @_(r'\n')
    def ignore_newline(self, t):
        self.lineno += 1

    @_(r'//.*\n')
    def ignore_comment(self, t):
        self.lineno += 1
        
    LEFT_PAREN = r'\('
    RIGHT_PAREN = r'\)'
    LEFT_BRACE = r'{'
    RIGHT_BRACE = r'}'
    COMMA = r','
    DOT = r'\.'
    MINUS = r'-'
    PLUS = r'\+'
    STAR = r'\*'
    SLASH = r'/'
    SEMI = r';'
    EQUAL_EQUAL = r'=='
    EQUAL = r'='
    BANG_EQUAL = r'!='
    BANG = r'!'
    LESS_EQUAL = r'<='
    LESS = r'<'
    GREATER_EQUAL = r'>='
    GREATER = r'>'

    @_(r'\d+(\.\d+)?')
    def NUMBER(self, t):
        t.value = float(t.value)
        return t

    @_(r'"(.|\n)*?"')
    def STRING(self, t):
        self.lineno += t.value.count('\n')
        t.value = t.value[1:-1]
        return t

    IDENTIFIER = r'[a-zA-Z_][a-zA-Z0-9_]*'
    IDENTIFIER['and'] = AND
    IDENTIFIER['class'] = CLASS
    IDENTIFIER['else'] = ELSE
    IDENTIFIER['false'] = FALSE
    IDENTIFIER['for'] = FOR
    IDENTIFIER['fun'] = FUN
    IDENTIFIER['if'] = IF
    IDENTIFIER['nil'] = NIL
    IDENTIFIER['or'] = OR
    IDENTIFIER['print'] = PRINT
    IDENTIFIER['return'] = RETURN
    IDENTIFIER['super'] = SUPER
    IDENTIFIER['this'] = THIS
    IDENTIFIER['true'] = TRUE
    IDENTIFIER['var'] = VAR
    IDENTIFIER['while'] = WHILE

    def error(self, t):
        print(f'{self.lineno}: Illegal character {t.value[0]!r}')
        self.index += 1

def test_scanner():
    lexer = LoxLexer()
    tokens = lexer.tokenize("""( ) { } , . - + * = ==
                            // This is a comment
                            / ; ! != < <= > >=""")
    toktypes = [t.type for t in tokens]
    assert toktypes == [ 'LEFT_PAREN', 'RIGHT_PAREN', 'LEFT_BRACE', 'RIGHT_BRACE',
                         'COMMA', 'DOT', 'MINUS', 'PLUS', 'STAR', 'EQUAL', 'EQUAL_EQUAL', 'SLASH',
                         'SEMI', 'BANG', 'BANG_EQUAL', 'LESS', 'LESS_EQUAL',
                         'GREATER', 'GREATER_EQUAL']

    tokens = lexer.tokenize("and class else false for fun if nil or print return super this true var while")
    toktypes = [t.type for t in tokens]
    assert toktypes == [ 'AND', 'CLASS', 'ELSE', 'FALSE', 'FOR', 'FUN', 'IF', 'NIL',
                         'OR', 'PRINT', 'RETURN', 'SUPER', 'THIS', 'TRUE',
                         'VAR', 'WHILE' ]

    tokens = lexer.tokenize('123 123.0 "hello" "hello\nworld"')
    tokvals = [(t.type, t.value) for t in tokens ]
    assert tokvals == [ ('NUMBER', 123), ('NUMBER', 123.0),
                        ('STRING', 'hello'), ('STRING', 'hello\nworld')]

    tokens = lexer.tokenize('abc abc123 _abc_123')
    tokvals = [(t.type, t.value) for t in tokens ]
    assert tokvals == [ ('IDENTIFIER', 'abc'), ('IDENTIFIER', 'abc123'), ('IDENTIFIER', '_abc_123')]
    
if __name__ == '__main__':
    test_scanner()
    
        
