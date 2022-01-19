# loxast.py

class Node:
    # Track define AST node-names for some later sanity checks
    _nodenames = set()
    @classmethod
    def __init_subclass__(cls):
        Node._nodenames.add(cls.__name__)

    _fields = []
    def __init__(self, *args):
        assert len(args) == len(type(self)._fields)
        for name, val in zip(type(self)._fields, args):
            setattr(self, name, val)
            
    def __repr__(self):
        args = ', '.join(f'{key}={value!r}' for key, value in vars(self).items())
        return f'{type(self).__name__}({args})'

    def __eq__(self, other):
        return type(self) == type(other) and vars(self) == vars(other)

# -- Expressions represent values
class Expression(Node):
    pass

class Literal(Expression):
    _fields = ['value']

class Binary(Expression):
    _fields = ['left', 'op', 'right']

class Logical(Expression):
    _fields = ['left', 'op', 'right']
        
class Unary(Expression):
    _fields = ['op', 'operand']
    
class Grouping(Expression):
    _fields = ['value']

class Variable(Expression):
    _fields = ['name']

class Assign(Expression):
    _fields = ['name', 'value']

class Call(Expression):
    _fields = ['func', 'arguments']

class Get(Expression):
    _fields = ['object', 'name']

class Set(Expression):
    _fields = ['object', 'name', 'value']

class This(Expression):
    _fields = [ ]

class Super(Expression):
    _fields = [ ]
    
# -- Statements represent actions with no associated value
class Statement(Node):
    pass

class Print(Statement):
    _fields = ['value']

class ExprStmt(Statement):
    _fields = ['value']
        
class IfStmt(Statement):
    _fields = ['test', 'consequence', 'alternative']

class WhileStmt(Statement):
    _fields = ['test', 'body']

class Return(Statement):
    _fields = ['value']
        
class Statements(Statement):
    _fields = ['statements']

# -- Declarations are special kinds of statements that declare the existence of something
class Declaration(Statement):
    pass

class VarDeclaration(Declaration):
    _fields = ['name', 'initializer']

class FuncDeclaration(Declaration):
    _fields = ['name', 'parameters', 'statements']

class ClassDeclaration(Declaration):
    _fields = ['name', 'superclass', 'methods']
    
# -- Visitor class
class NodeVisitor:
    @classmethod
    def __init_subclass__(cls):
        # Verify that any visit_* method actually corresponds to the name of an AST node.
        visitors = { key for key in cls.__dict__ if key.startswith('visit_') }
        assert all(key[6:] in Node._nodenames for key in visitors)
        
    def visit(self, node):
        method = f'visit_{type(node).__name__}'
        return getattr(self, method)(node)

# Debugging class for turning the AST into S-expressions
class ASTPrinter(NodeVisitor):
    def visit_Statements(self, node):
        return '(statements ' + ' '.join(self.visit(stmt) for stmt in node.statements) + ')'

    def visit_Print(self, node):
        return f'(print {self.visit(node.value)})'

    def visit_ExprStmt(self, node):
        return f'(exprstmt {self.visit(node.value)})'

    def visit_VarDeclaration(self, node):
        return f'(var {node.name} {self.visit(node.initializer)})' if node.initializer else f'(var {node.name})'

    def visit_IfStmt(self, node):
        if node.alternative:
            return f'(if {self.visit(node.test)} {self.visit(node.consequence)} {self.visit(node.alternative)})'
        else:
            return f'(if {self.visit(node.test)} {self.visit(node.consequence)})'

    def visit_WhileStmt(self, node):
        return f'(while {self.visit(node.test)} {self.visit(node.body)})'
    
    def visit_Assign(self, node):
        return f'(assign {node.name} {self.visit(node.value)})'
    
    def visit_Literal(self, node):
        if node.value is None:
            return "nil"
        elif node.value is True:
            return "true"
        elif node.value is False:
            return "false"
        else:
            return repr(node.value)

    def visit_Variable(self, node):
        return node.name
    
    def visit_Binary(self, node):
        return f'({node.op} {self.visit(node.left)} {self.visit(node.right)})'

    visit_Logical = visit_Binary
    
    def visit_Unary(self, node):
        return f'({node.op} {self.visit(node.operand)})'

    def visit_Grouping(self, node):
        return f'(group {self.visit(node.value)})'

    def visit_Call(self, node):
        return f'(call {self.visit(node.func)} ' + ' '.join(self.visit(arg) for arg in node.arguments) + ')'

    def visit_Return(self, node):
        return f'(return {self.visit(node.value)})'

    def visit_FuncDeclaration(self, node):
        return f'(func {node.name} {node.parameters} {self.visit(node.statements)})'

    def visit_Get(self, node):
        return f'(get {self.visit(node.object)} {node.name})'

    def visit_Set(self, node):
        return f'(set {self.visit(node.object)} {node.name} {self.visit(node.value)})'

    def visit_ClassDeclaration(self, node):
        return f'(class {node.name} {node.superclass} ' + ' '.join(self.visit(meth) for meth in node.methods) + ')'

    def visit_This(self, node):
        return 'this'

    def visit_Super(self, node):
        return 'super'
    
    
    

    


